# -*- coding: utf-8 -*-

"""
This extension will work with Network Manager VPN's via nmcli
Provide simple way to turn VPN on/off from Albert interface
"""

from albertv0 import *
import subprocess
import os


__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Network Manager VPN"
__version__ = "0.1"
__trigger__ = "vpn "
__author__ = "Igor Olhovskiy"
__dependencies__ = []

def handleQuery(query):
    if query.isTriggered:

        results = []

        cmd = ['nmcli', '-t', 'connection', 'show']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = p.communicate()

        if err is not None:
            return Item(
                text='Error',
                subtext=err
            )
        
        lines = out.splitlines()
        
        for line in lines:

            # Splitlines returns object as bytearray.
            line = line.decode('utf-8')

            if_name, if_uuid, if_type, if_device = line.split(':')

            if if_type == 'vpn' and query.string in if_name:

                if len(if_device) == 0: # Disconnected
                    if_status_text = "Connect " + if_name
                    if_icon = os.path.dirname(__file__)+"/connect.svg"
                    if_action = [ProcAction("Connecting {}...".format(if_name), ["nmcli", "connection", "up", if_uuid])]
                else:
                    if_status_text = "Disconnect " + if_name
                    if_icon = os.path.dirname(__file__)+"/disconnect.svg"
                    if_action = [ProcAction("Disconnecting {}...".format(if_name), ["nmcli", "connection", "down", if_uuid])]                
                    
                results.append(
                    Item(
                        icon = if_icon,
                        text = if_name.replace(query.string, "<u>%s</u>" % query.string),
                        subtext = if_status_text,
                        completion = __trigger__ + if_name,
                        actions = if_action
                    )
                )
        
        return results