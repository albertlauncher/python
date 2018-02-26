# -*- coding: utf-8 -*-

"""
Use machinelearning to find the relevant emoji.
If your emojis are not rendering properly go to and install the emoji fonts at the following link: 
https://github.com/eosrei/emojione-color-font
"""

from albertv0 import *
import json
import os
import urllib.request
import urllib.parse
import urllib.error
import requests

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Dango Emoji"
__version__ = "1.0"
__trigger__ = "emoji "
__author__ = "David Britt"
__dependencies__ = []

icon_path = os.path.dirname(__file__) + "/emojicon.svg"
dangoUrl = "https://emoji.getdango.com/api/emoji"

def handleQuery(query):
	results = []
	if query.isTriggered:

		item = Item(
            id=__prettyname__,
            icon=icon_path,
            completion=query.rawString,
            text=__prettyname__,
            actions=[]
		)

		if len(query.string) >= 2:
			try:
				with requests.get(dangoUrl, params={"q": query.string}) as api_response:
					json_data = json.loads(api_response.text)

					all_emojis = []
					for emoj in json_data["results"]:
						all_emojis.append(emoj["text"])

					string_emojis = ''.join(all_emojis)

					results.append(Item(
					    id=__prettyname__,
	                    icon=icon_path,
	                    text=string_emojis,
	                    actions=[
	                        ClipAction("Copy translation to clipboard", string_emojis)
	                    ]
					))

					for emoj in json_data["results"]:
						results.append(
							Item(
								    id=__prettyname__,
                                    icon=icon_path,
                                    text=str(emoj["text"]),
                                    actions=[
                                        ClipAction("Copy translation to clipboard", str(emoj["text"]))
                                    ]
							)	
						)

			except urllib.error.URLError as urlerr:
				print("Troubleshoot internet connection: %s" % urlerr)
				item.subtext = "Connection error"
				return item
		else:
			item.subtext = "Search emojis!"
			return item
	return results