# -*- coding: utf-8 -*-

"""Offline Unicode emoji picker.

Synopsis: <trigger> [filter]"""

#  Copyright (c) 2022 Manuel Schneider

from albert import *
from collections import namedtuple
from threading import Thread
import datetime
import os
import subprocess
import urllib.request
import shutil

__title__ = "Unicode Emojis"
__version__ = "0.4.3"
__triggers__ = ":"
__authors__ = ["Tim Zeitz", "Manuel S."]
__exec_deps__ = ["convert"]

EmojiSpec = namedtuple('EmojiSpec', ['string', 'name', 'modifiers'])
emoji_data_src_url = "https://unicode.org/Public/emoji/latest/emoji-test.txt"
emoji_data_path = os.path.join(dataLocation(), "emoji.txt")
icon_path_template = os.path.join(cacheLocation(), __name__, "%s.png")
emojiSpecs = []
thread = None


class WorkerThread(Thread):
    def __init__(self):
        super().__init__()
        self.stop = False

    def run(self):

        # Create cache dir
        cache_dir_path = os.path.join(cacheLocation(), __name__)
        if not os.path.exists(cache_dir_path):
            os.mkdir(cache_dir_path)

        # Build the index and icon cache
        # global emojiSpecs
        emojiSpecs.clear()
        with open(emoji_data_path) as f:
            for line in f:
                if "; fully-qualified" in line:
                    emoji, desc = line.split('#', 1)[-1].split(None, 1)
                    desc = [d.strip().lower() for d in desc.split(':')]
                    emojiSpecs.append(EmojiSpec(emoji, desc[0], desc[1] if len(desc)==2 else ""))

                    icon_path = icon_path_template % emoji
                    if not os.path.exists(icon_path):
                        subprocess.call(["convert", "-pointsize", "64", "-background", "transparent", "pango:%s" % emoji, icon_path])

                if self.stop:
                    return

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
        warning(e)

    # Build the index and icon cache
    global thread
    thread = WorkerThread()
    thread.start()

def finalize():
    global thread
    if thread is not None:
        thread.stop = True
        thread.join()

def get_emoji_data_version(path):
    with open(emoji_data_path) as f:
        for line in f:
            if "# Date: " in line:
                return datetime.datetime.strptime(line.strip(), "# Date: %Y-%m-%d, %H:%M:%S GMT")

def handleQuery(query):
    if query.isValid and query.isTriggered:
        items = []
        query_tokens = query.string.lower().split()
        # filter emojiSpecs where all query words are in any of the emoji description words
        for es in filter(lambda e: all(any(n in s for s in [e.name, e.modifiers]) for n in query_tokens), emojiSpecs):
            items.append(Item(id = "%s%s" % (__name__, es.string),
                              completion = es.name if not es.modifiers else " ".join([es.name, es.modifiers]),
                              icon = icon_path_template % es.string,
                              text = es.name.capitalize(),
                              subtext = es.modifiers.capitalize() if es.modifiers else "<i>(No modifiers)</i>",
                              actions = [ClipAction("Copy to clipboard", es.string)]))
        return items
