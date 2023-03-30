# -*- coding: utf-8 -*-

import virtualbox
from virtualbox.library import LockType, MachineState

from albert import *

md_iid = "0.5"
md_version = "1.3"
md_name = "VirtualBox"
md_description = "Manage your VirtualBox machines"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/virtualbox"
md_maintainers = "@manuelschneid3r"
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
        session.machine.discard_save_state(True);

def resumeVm(vm):
    with vm.create_session(LockType.shared) as session:
        session.console.resume()

def pauseVm(vm):
    with vm.create_session(LockType.shared) as session:
        session.console.pause()

class Plugin(QueryHandler):
    iconUrls = ["xdg:virtualbox", ":unknown"]

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def synopsis(self):
        return "<machine name>"

    def defaultTrigger(self):
        return "vbox "

    def handleQuery(self, query):
        items = []
        pattern = query.string.strip().lower()
        try:
            for vm in filter(lambda vm: pattern in vm.name.lower(), virtualbox.VirtualBox().machines):
                actions = []
                if vm.state == MachineState.powered_off or vm.state == MachineState.aborted:  #1 #4
                    actions.append(Action("startvm", "Start virtual machine", lambda vm=vm: startVm(vm)))
                if vm.state == MachineState.saved:  #2
                    actions.append(Action("restorevm", "Start saved virtual machine", lambda vm=vm: startVm(vm)))
                    actions.append(Action("discardvm", "Discard saved state", lambda vm=vm: discardSavedVm(vm)))
                if vm.state == MachineState.running:  #5
                    actions.append(Action("savevm", "Save virtual machine", lambda vm=vm: saveVm(vm)))
                    actions.append(Action("poweroffvm", "Power off via ACPI event (Power button)", lambda vm=vm: acpiPowerVm(vm)))
                    actions.append(Action("stopvm", "Turn off virtual machine", lambda vm=vm: stopVm(vm)))
                    actions.append(Action("pausevm", "Pause virtual machine", lambda vm=vm: pauseVm(vm)))
                if vm.state == MachineState.paused:  #6
                    actions.append(Action("resumevm", "Resume virtual machine", lambda vm=vm: resumeVm(vm)))

                items.append(
                    Item(
                        id=vm.__uuid__,
                        text=vm.name,
                        subtext="{vm.state}".format(vm=vm),
                        completion=vm.name,
                        icon=self.iconUrls,
                        actions=actions
                    )
                )
        except Exception as e:
            warning(str(e))

        query.add(items)
