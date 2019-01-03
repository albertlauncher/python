# -*- coding: utf-8 -*-

"""VirtualBox extension.

Manage your virtual machines."""

from virtualbox import Session, VirtualBox
from virtualbox.library import (LockType, MachineState, OleErrorInvalidarg,
                                OleErrorUnexpected, VBoxErrorFileError,
                                VBoxErrorHostError,
                                VBoxErrorInvalidObjectState,
                                VBoxErrorInvalidVmState, VBoxErrorIprtError,
                                VBoxErrorObjectNotFound)

from albertv0 import FuncAction, Item, critical, iconLookup

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Virtual Box"
__version__ = "1.2"
__trigger__ = "vbox "
__author__ = "Manuel Schneider"
__dependencies__ = ['pyvbox']

vbox = None

for iconName in ["virtualbox", "unknown"]:
    iconPath = iconLookup(iconName)
    if iconPath:
        break

def initialize():
    global vbox
    vbox = VirtualBox()

def finalize():
    pass

def startVm(vm):
    try:
        with Session() as session:
            vm.launch_vm_process(session, 'gui', '')
    except OleErrorUnexpected as e:
        warning("OleErrorUnexpected")
    except OleErrorInvalidarg as e:
        warning("OleErrorInvalidarg")
    except VBoxErrorObjectNotFound as e:
        warning("VBoxErrorObjectNotFound")
    except VBoxErrorInvalidObjectState as e:
        warning("VBoxErrorInvalidObjectState")
    except VBoxErrorInvalidVmState as e:
        warning("VBoxErrorInvalidVmState")
    except VBoxErrorIprtError as e:
        warning("VBoxErrorIprtError")
    except VBoxErrorHostError as e:
        warning("VBoxErrorHostError")
    except  VBoxErrorFileError as e:
        warning("VBoxErrorFileError")

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

def buildVmItem(vm):
    item = Item(
        id=vm.__uuid__,
        icon=iconPath,
        text=vm.name,
        subtext="{vm.state}".format(vm=vm),
        completion=vm.name
    )

    if vm.state == MachineState.powered_off:  #1
        item.addAction(FuncAction(text="Start virtual machine", callable=lambda: startVm(vm)))
    if vm.state == MachineState.saved:  #2
        item.addAction(FuncAction(text="Restore virtual machine", callable=lambda: startVm(vm)))
        item.addAction(FuncAction(text="Discard saved state", callable=lambda: discardSavedVm(vm)))
    if vm.state == MachineState.aborted:  #4
        item.addAction(FuncAction(text="Start virtual machine", callable=lambda: startVm(vm)))
    if vm.state == MachineState.running:  #5
        item.addAction(FuncAction(text="Save virtual machine", callable=lambda: saveVm(vm)))
        item.addAction(FuncAction(text="Power off via ACPI event (Power button)", callable=lambda: acpiPowerVm(vm)))
        item.addAction(FuncAction(text="Turn off virtual machine", callable=lambda: stopVm(vm)))
        item.addAction(FuncAction(text="Pause virtual machine", callable=lambda: pauseVm(vm)))
    if vm.state == MachineState.paused:  #6
        item.addAction(FuncAction(text="Resume virtual machine", callable=lambda: resumeVm(vm)))

    return item


def handleQuery(query):
    pattern = query.string.strip().lower()
    results = []
    try:
        for vm in vbox.machines:
            if (pattern and pattern in vm.name.lower() or not pattern and query.isTriggered):
                results.append(buildVmItem(vm))
    except Exception as e:
        critical(str(e))
    return results
