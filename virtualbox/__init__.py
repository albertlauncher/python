# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider
"""
This plugin is based on [virtualbox-python](https://pypi.org/project/virtualbox/) and needs the 'vboxapi' module which
is part of the VirtualBox SDK. Some distributions package the SDK, e.g. Arch has
[virtualbox-sdk](https://archlinux.org/packages/extra/x86_64/virtualbox-sdk/).
"""

import virtualbox
from virtualbox.library import LockType, MachineState

from albert import *

md_iid = "3.0"
md_version = "2.0"
md_name = "VirtualBox"
md_description = "Manage your VirtualBox machines"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/virtualbox"
md_authors = "@manuelschneid3r"
md_lib_dependencies = ['virtualbox']


def startVm(vm):
    try:
        with virtualbox.Session() as session:
            progress = vm.launch_vm_process(session, 'gui', [])
            progress.wait_for_completion()
    except Exception as e:
        warning(str(e))


def acpiPowerVm(vm):
    with vm.create_session(LockType.shared) as session:
        session.console.power_button()


def stopVm(vm):
    with vm.create_session(LockType.shared) as session:
        session.console.power_down()


def saveVm(vm):
    with vm.create_session(LockType.shared) as session:
        session.machine.save_state()


def discardSavedVm(vm):
    with vm.create_session(LockType.shared) as session:
        session.machine.discard_save_state(True)


def resumeVm(vm):
    with vm.create_session(LockType.shared) as session:
        session.console.resume()


def pauseVm(vm):
    with vm.create_session(LockType.shared) as session:
        session.console.pause()


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)
        self.iconUrls = ["xdg:virtualbox", ":unknown"]

    def defaultTrigger(self):
        return 'vbox '

    def synopsis(self, query):
        return "<machine name>"

    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip(),
                'widget_properties': {
                    'textFormat': 'Qt::MarkdownText'
                }
            }
        ]

    def handleTriggerQuery(self, query):
        items = []
        pattern = query.string.strip().lower()
        try:
            for vm in filter(lambda vm: pattern in vm.name.lower(), virtualbox.VirtualBox().machines):
                actions = []
                if vm.state == MachineState.powered_off or vm.state == MachineState.aborted:  # 1 # 4
                    actions.append(Action("startvm", "Start virtual machine", lambda m=vm: startVm(m)))
                if vm.state == MachineState.saved:  # 2
                    actions.append(Action("restorevm", "Start saved virtual machine", lambda m=vm: startVm(m)))
                    actions.append(Action("discardvm", "Discard saved state", lambda m=vm: discardSavedVm(m)))
                if vm.state == MachineState.running:  # 5
                    actions.append(Action("savevm", "Save virtual machine", lambda m=vm: saveVm(m)))
                    actions.append(Action("poweroffvm", "Power off via ACPI event (Power button)", lambda m=vm: acpiPowerVm(m)))
                    actions.append(Action("stopvm", "Turn off virtual machine", lambda m=vm: stopVm(m)))
                    actions.append(Action("pausevm", "Pause virtual machine", lambda m=vm: pauseVm(m)))
                if vm.state == MachineState.paused:  # 6
                    actions.append(Action("resumevm", "Resume virtual machine", lambda m=vm: resumeVm(m)))

                items.append(
                    StandardItem(
                        id=vm.__uuid__,
                        text=vm.name,
                        subtext="{vm.state}".format(vm=vm),
                        inputActionText=vm.name,
                        iconUrls=self.iconUrls,
                        actions=actions
                    )
                )
        except Exception as e:
            warning(str(e))

        query.add(items)
