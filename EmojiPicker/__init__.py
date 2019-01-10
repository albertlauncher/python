# -*- coding: utf-8 -*-

"""Emoji Picker for Albert
Usage: :<emoji name>
Example: :see no evil"""

from albertv0 import *

import os
import shutil
import urllib.request
import datetime

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Albert Emoji Picker"
__version__ = "0.2.0"
__trigger__ = ":"
__author__ = "Tim 'S.D.Eagle' Zeitz"
__dependencies__ = []

emoji_data_src_url = "https://unicode.org/Public/emoji/latest/emoji-test.txt"
emoji_data_path = os.path.join(dataLocation(), "emoji.txt")

emojis = []

def initialize():
    src_directory = os.path.dirname(os.path.realpath(__file__))

    # if no emoji data exists copy offline src as fallback
    if not os.path.isfile(emoji_data_path):
        shutil.copyfile(os.path.join(src_directory, "emoji.txt"), emoji_data_path)

    current_version = get_emoji_data_version(emoji_data_path)

    try:
        new_path = os.path.join(dataLocation(), "emoji-new.txt")

        # try to fetch the latest emoji data
        with urllib.request.urlopen(emoji_data_src_url) as response, open(new_path, 'wb') as out_file:
            # save it
            shutil.copyfileobj(response, out_file)

        # update emoji data if the fetched data is newer
        if get_emoji_data_version(new_path) > current_version:
            shutil.copyfile(new_path, emoji_data_path)

        os.remove(new_path)

    except Exception as e:
        warn(e)

    build_index()

def get_emoji_data_version(path):
    with open(emoji_data_path) as f:
        for line in f:
            if "# Date: " in line:
                return datetime.datetime.strptime(line.strip(), "# Date: %Y-%m-%d, %H:%M:%S GMT")

def build_index():
    emojis.clear()

    with open(emoji_data_path) as f:
        for line in f:
            if "; fully-qualified" in line:
                [emoji, name] = line.split('#', 1)[-1].split(None, 1)
                emojis.append((emoji, name.strip(), name.lower().split()))

def handleQuery(query):
    if query.isValid and query.isTriggered:
        return [Item(id=key, completion=key, icon=emoji, text=emoji, subtext=key, actions=[ClipAction("Copy to clipboard", emoji)]) for (emoji, key, matchcount) in matches(query.string.lower().split())]
    return []

def matches(needles):
    matched = [(emoji, name, count_matches(tokens, needles)) for (emoji, name, tokens) in emojis]
    matched = [(emoji, name, matchcount) for (emoji, name, matchcount) in matched if matchcount > 0]
    matched = sorted(matched, key=lambda data: data[2], reverse=True)
    return matched

def count_matches(tokens, needles):
    count = 0
    for token in tokens:
        for needle in needles:
            if needle in token:
                count += 1
    return count
