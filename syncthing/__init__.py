# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider

"""
Quickly pause/resume/open/scan shares and devices.
"""

from pathlib import Path

from albert import *
from syncthing import Syncthing

md_iid = '2.3'
md_version = "1.0"
md_name = "Syncthing"
md_description = "Trigger basic syncthing actions."
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/main/syncthing"
md_authors = "@manuelschneid3r"
md_lib_dependencies = "syncthing"


class Plugin(PluginInstance, GlobalQueryHandler):

    config_key = 'syncthing_api_key'

    def __init__(self):
        PluginInstance.__init__(self)
        GlobalQueryHandler.__init__(self, self.id, self.name, self.description, defaultTrigger='st ')
        self.iconUrls = ["xdg:syncthing", f"file:{Path(__file__).parent}/syncthing.svg"]
        self._api_key = self.readConfig(self.config_key, str)
        if self._api_key:
            self.st = Syncthing(self._api_key)

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        if self._api_key != value:
            self._api_key = value
            self.writeConfig(self.config_key, value)
            self.st = Syncthing(self._api_key)


    def configWidget(self):
        return [
            {
                'type': 'label',
                'text': __doc__.strip(),
            },
            {
                'type': 'lineedit',
                'property': 'api_key',
                'label': 'API key',
                'widget_properties': {'tooltip': 'You can find the API key using the web frontend.'}
            }
        ]

    def handleGlobalQuery(self, query):

        results = []

        if self.st:

            config = self.st.system.config()

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

            matcher = Matcher(query.string)

            # create device items
            for id, d in devices.items():
                device_name = d['name']

                if match := matcher.match(device_name):
                    device_folders = ", ".join([f['label'] for f in d['_shared_folders'].values()])

                    actions = []
                    if d['paused']:
                        actions.append(
                            Action("resume", "Resume synchronization",
                                   lambda did=id: self.st.system.resume(did))
                        )
                    else:
                        actions.append(
                            Action("pause", "Pause synchronization",
                                   lambda did=id: self.st.system.pause(did))
                        )

                    results.append(
                        RankItem(
                            StandardItem(
                                id=id,
                                text=f"{device_name}",
                                subtext=f"{'Paused ' if d['paused'] else ''}Syncthing device. "
                                        f"Shared: {device_folders if device_folders else 'Nothing'}.",
                                iconUrls=self.iconUrls,
                                actions=actions
                            ),
                            match.score
                        )
                    )

            # create folder items
            for id, f in folders.items():
                folder_name = f['label']
                if match := matcher.match(folder_name):
                    folders_devices = ", ".join([devices[d['deviceID']]['name'] for d in f['devices']])
                    results.append(
                        RankItem(
                            StandardItem(
                                id=id,
                                text=folder_name,
                                subtext=f"Syncthing folder {f['path']}. "
                                        f"Shared with {folders_devices if folders_devices else 'nobody'}.",
                                iconUrls=self.iconUrls,
                                actions=[
                                    Action("scan", "Scan the folder",
                                           lambda fid=id: self.st.database.scan(fid)),
                                    Action("open", "Open this folder in file browser",
                                           lambda p=f['path']: openUrl(f'file://{p}'))
                                ]
                            ),
                            match.score
                        )
                    )

        return results
