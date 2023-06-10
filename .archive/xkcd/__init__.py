"""Fetch xkcd comics like a boss."""

#  Copyright (c) 2022 Manuel Schneider

from datetime import datetime, timedelta
from pathlib import Path
import json
import os
import subprocess
import sys

import albertv0 as v0
from fuzzywuzzy import process
from shutil import which

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "xkcd"
__version__ = "0.1"
__trigger__ = "xkcd"
__author__ = "Nikos Koukis"
__dependencies__ = []
__homepage__ = "https://github.com/bergercookie/xkcd-albert-plugin"


# TODO pyproject toml file
# TODO xkcd-dl executable?
# TODO Upload to github - change support url on error
# TODO Send to albert plugins

if not which("xkcd-dl"):
    raise RuntimeError("xkcd-dl not in $PATH - Please install it via pip3 first.")

iconPath = v0.iconLookup("xkcd")
if not iconPath:
    iconPath = os.path.join(os.path.dirname(__file__), "image.png")
SETTINGS_PATH = Path(v0.cacheLocation()) / "xkcd"
LAST_UPDATE_PATH = SETTINGS_PATH / "last_update"
XKCD_DICT = Path.home() / ".xkcd_dict.json"


def initialize():
    # Called when the extension is loaded (ticked in the settings) - blocking

    # create cache location
    SETTINGS_PATH.mkdir(parents=False, exist_ok=True)
    if not LAST_UPDATE_PATH.is_file():
        update_date_file()
        update_xkcd_db()


def finalize():
    pass


def handleQuery(query):
    results = []

    # check whether I have downlaoded the latest metadata
    with open(LAST_UPDATE_PATH, "r") as f:
        date_str = float(f.readline().strip())

    last_date = datetime.fromtimestamp(date_str)
    if datetime.now() - last_date > timedelta(days=1):  # run an update daily
        update_date_file()
        update_xkcd_db()

    if query.isTriggered:
        try:
            with open(XKCD_DICT, "r", encoding="utf-8") as f:
                d = json.load(f)

            if len(query.string) in [0, 1]:  # Display all items
                for k, v in d.items():
                    results.append(get_as_item(k, v))
            else:  # fuzzy search
                desc_to_item = {item[1]["description"]: item for item in d.items()}
                matched = process.extract(
                    query.string.strip(), list(desc_to_item.keys()), limit=20
                )
                for m in [elem[0] for elem in matched]:
                    # bypass a unicode issue - use .get
                    item = desc_to_item.get(m)
                    if item:
                        results.append(get_as_item(*item))

        except Exception as e:  # user to report error
            results.insert(
                0,
                v0.Item(
                    id=__prettyname__,
                    icon=iconPath,
                    text="Something went wrong! Press [ENTER] to copy error and report it",
                    actions=[
                        v0.ClipAction(
                            f"Copy error - report it to {__homepage__[8:]}",
                            f"{sys.exc_info()}",
                        )
                    ],
                ),
            )

    return results


def get_as_item(k: str, v: dict):
    return v0.Item(
        id=__prettyname__,
        icon=iconPath,
        text=v["description"],
        subtext=v["date-published"],
        completion="",
        actions=[
            v0.UrlAction("Open in xkcd.com", f"https://www.xkcd.com/{k}"),
            v0.ClipAction("Copy URL", f"https://www.xkcd.com/{k}"),
        ],
    )


def update_date_file():
    now = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
    with open(LAST_UPDATE_PATH, "w") as f:
        f.write(str(now))


def update_xkcd_db():
    return subprocess.call(["xkcd-dl", "-u"])
