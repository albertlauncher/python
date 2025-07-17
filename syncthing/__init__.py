# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

import json
import urllib.error
import urllib.request
from pathlib import Path

from albert import *

md_iid = "3.0"
md_version = "3.0"
md_name = "Syncthing"
md_description = "Control the local Syncthing instance."
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/syncthing"
md_authors = "@manuelschneid3r"


# https://docs.syncthing.net/dev/rest.html
class Syncthing:
    def __init__(self, api_key, base_url="http://localhost:8384"):
        self.api_key = api_key
        self.base_url = base_url

    def _request(self, method, endpoint, data=None) -> dict:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                if not (200 <= resp.status < 300):
                    raise Exception(f"Unexpected status {resp.status}")
                content = resp.read().decode()
                return json.loads(content) if content else {}
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP {e.code}: {e.read().decode()}")

    def _get(self, endpoint):
        return self._request("GET", endpoint)

    def _post(self, endpoint, data=None):
        return self._request("POST", endpoint, data)

    def _patch(self, endpoint, data=None):
        return self._request("PATCH", endpoint, data)

    def config(self):
        return self._get('/rest/config')

    def resumeDevice(self, device_id:str):
        return self._patch(f'/rest/config/devices/{device_id}', {'paused': False})

    def pauseDevice(self, device_id:str):
        return self._patch(f'/rest/config/devices/{device_id}', {'paused': True})

    def resumeFolder(self, folder_id:str):
        return self._patch(f'/rest/config/folders/{folder_id}', {'paused': False})

    def pauseFolder(self, folder_id:str):
        return self._patch(f'/rest/config/folders/{folder_id}', {'paused': True})

    def scanFolder(self, folder_id:str):
        return self._post(f'/rest/db/scan?folder={folder_id}')


class Plugin(PluginInstance, GlobalQueryHandler):

    config_key = 'syncthing_api_key'
    icon_urls_active = [f"file:{Path(__file__).parent}/syncthing_active.svg"]
    icon_urls_inactive = [f"file:{Path(__file__).parent}/syncthing_inactive.svg"]

    def __init__(self):
        PluginInstance.__init__(self)
        GlobalQueryHandler.__init__(self)
        self.st = Syncthing(self.readConfig(self.config_key, str) or '')

    def defaultTrigger(self):
        return 'st '

    @property
    def api_key(self) -> str:
        return self.st.api_key

    @api_key.setter
    def api_key(self, value: str):
        if self.st.api_key != value:
            self.st.api_key = value
            self.writeConfig(self.config_key, value)

    def configWidget(self):
        return [
            {
                'type': 'lineedit',
                'property': 'api_key',
                'label': 'API key',
                'widget_properties': {'tooltip': 'You can find the API key using the web frontend.'}
            }
        ]

    def handleTriggerQuery(self, query):
        try:
            super().handleTriggerQuery(query)
        except Exception as e:
            query.add(StandardItem(id="err", text="Error", subtext=str(e), iconUrls=self.icon_urls_active))

    def handleGlobalQuery(self, query):

        config = self.st.config()

        devices = dict()
        for d in config['devices']:
            if not d['name']:
                d['name'] = d['deviceID']
            d['_shared_folders'] = {}
            devices[d['deviceID']] = d

        folders = dict()
        for f in config['folders']:
            if not f['label']:
                f['label'] = f['id']
            for d in f['devices']:
                devices[d['deviceID']]['_shared_folders'][f['id']] = f
            folders[f['id']] = f

        results = []
        matcher = Matcher(query.string)

        # create device items
        for device_id, d in devices.items():
            device_name = d['name']

            if match := matcher.match(device_name):
                device_folders = ", ".join([f['label'] for f in d['_shared_folders'].values()])

                actions = []
                if d['paused']:
                    actions.append(Action("resume", "Resume", lambda did=device_id: self.st.resumeDevice(did)))
                else:
                    actions.append(Action("pause", "Pause", lambda did=device_id: self.st.pauseDevice(did)))

                item = StandardItem(
                    id=device_id,
                    text=f"{device_name}",
                    subtext=f"{'PAUSED · ' if d['paused'] else ''}Device · "
                            f"Shared: {device_folders if device_folders else 'Nothing'}.",
                    iconUrls=self.icon_urls_inactive if d['paused'] else self.icon_urls_active,
                    actions=actions
                )

                results.append(RankItem(item, match))

        # create folder items
        for folder_id, f in folders.items():
            folder_name = f['label']
            if match := matcher.match(folder_name):
                folders_devices = ", ".join([devices[d['deviceID']]['name'] for d in f['devices']])

                actions = []
                if f['paused']:
                    actions.append(Action("resume", "Resume", lambda fid=folder_id: self.st.resumeFolder(fid)))
                else:
                    actions.append(Action("pause", "Pause", lambda fid=folder_id: self.st.pauseFolder(fid)))
                actions.append(Action("open", "Open", lambda p=f['path']: openFile(p)))
                actions.append(Action("scan", "Scan", lambda fid=folder_id: self.st.scanFolder(fid)))

                item = StandardItem(
                    id=folder_id,
                    text=folder_name,
                    subtext=f"{'PAUSED · ' if f['paused'] else ''}Folder · {f['path']} · "
                            f"Shared with {folders_devices if folders_devices else 'nobody'}.",
                    iconUrls=self.icon_urls_inactive if f['paused'] else self.icon_urls_active,
                    actions=actions
                )
                results.append(RankItem(item, match))

        return results
