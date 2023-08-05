# -*- coding: utf-8 -*-

import json
import re
import threading
import urllib.request
from itertools import product
from locale import getdefaultlocale
from pathlib import Path

from albert import *

md_iid = '2.0'
md_version = "2.0"
md_name = "Emoji"
md_description = "Find and copy emojis by name"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/master/emoji"


class Plugin(PluginInstance, IndexQueryHandler):

    def __init__(self):
        IndexQueryHandler.__init__(self,
                                   id=md_id,
                                   name=md_name,
                                   description=md_description,
                                   defaultTrigger=':',
                                   synopsis='<emoji name>')
        PluginInstance.__init__(self, extensions=[self])
        self.thread = None

    def finalize(self):
        if self.thread.is_alive():
            self.thread.join()

    def updateIndexItems(self):
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = threading.Thread(target=self.update_index_items_task)
        self.thread.start()

    def update_index_items_task(self):

        def download_file(url: str, path: str) -> bool:
            debug(f"Downloading {url}.")
            headers = {'User-Agent': 'Mozilla/5.0'}  # otherwise github returns html
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=3) as response:
                if response.getcode() == 200:
                    debug(f"Success. Storing to {path}.")
                    with open(path, 'wb') as file:
                        file.write(response.read())
                else:
                    raise RuntimeError(f"Failed to download {url}. Status code: {response.getcode()}")

        def get_fully_qualified_emojis(cache_path: str) -> list:
            """Returns fully qualified emoji strings"""

            def convert_to_unicode_char(hex_code: str):
                return chr(int(hex_code, 16))

            def convert_to_unicode_str(hex_codes: str):
                hex_list = hex_codes.split()
                return ''.join([convert_to_unicode_char(hex_code) for hex_code in hex_list])

            path = cache_path / 'emoji_list.txt'
            if not path.is_file():
                info("Fetching emoji list.")
                url = 'https://unicode.org/Public/emoji/latest/emoji-test.txt'
                download_file(url, path)

            # components = set()
            fully_qualified = []

            with path.open("r") as f:

                emoji_list_re_str = r"""
                         ^
                         (?P<codepoints> .*\S)
                         \s*;\s*
                         (?P<status> \S+)
                         \s*\#\s*
                         (?P<emoji> \S+)
                         \s*
                         (?P<version> E\d+.\d+)
                         \s*
                         (?P<name> [^:]+)
                         (?: : \s* (?P<modifier> .+))?
                         \n
                         $
                         """

                line_re = re.compile(emoji_list_re_str, re.VERBOSE)
                for line in f:
                    if match := line_re.match(line):
                        if match.group("status") == "fully-qualified":
                            fully_qualified.append(convert_to_unicode_str(match.group("codepoints")))

            return fully_qualified

        def get_annotations(cache_path: str) -> dict:

            # determine locale

            if lang := getdefaultlocale()[0]:
                lang = lang[0:2]
            else:
                warning("Failed getting locale. There will be no localized emoji aliases.")
                lang = 'en'

            # fetch localized cldr annotations 'full'

            path_full = cache_path / 'emoji_annotations_full.json'
            if not path_full.is_file():
                url = 'https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/' \
                      'cldr-annotations-full/annotations/%s/annotations.json' % lang
                download_file(url, path_full)

            # fetch localized cldr annotations 'derived'

            path_derived = cache_path / 'emoji_annotations_derived.json'
            if not path_derived.is_file():
                url = 'https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/' \
                      'cldr-annotations-derived-full/annotationsDerived/%s/annotations.json' % lang
                download_file(url, path_derived)

            # open, read, parse, merge, return

            with path_full.open("r", encoding='utf-8') as file_full, \
                    path_derived.open("r", encoding='utf-8') as file_derived:
                json_full = json.load(file_full)['annotations']['annotations']
                json_derived = json.load(file_derived)['annotationsDerived']['annotations']
                return json_full | json_derived
        emojis = get_fully_qualified_emojis(self.cacheLocation)
        annotations = get_annotations(self.cacheLocation)

        def remove_redundancy(sentences):
            sets_of_words = [set(sentence.lower().split()) for sentence in sentences]
            unique = []
            for sow, sentence in zip(sets_of_words, sentences):
                for other_sow in sets_of_words:
                    if sow != other_sow:
                        if all([any([oword.startswith(word) for oword in other_sow]) for word in sow]):
                            break
                else:
                    unique.append(sentence)
            return unique

        index_items = []
        for emoji in emojis:
            try:
                ann = annotations[emoji]
            except KeyError:
                try:
                    non_rgi_emoji = emoji.replace('\uFE0F', '')
                    ann = annotations[non_rgi_emoji]
                except KeyError as e:
                    debug(f"Found no translation for {e}. Emoji will not be available.")
                    continue

            title = ann['tts'][0]
            aliases = remove_redundancy([title.replace(':', '').replace(',', ''), *ann['default']])

            item = StandardItem(
                id=emoji,
                text=title.capitalize(),
                subtext=", ".join([a.capitalize() for a in aliases]),
                iconUrls=[f"gen:?text={emoji}"],
                actions=[
                    Action(
                        "copy",
                        "Copy to clipboard",
                        lambda emj=emoji: setClipboardText(emj),
                    ),
                ]
            )

            for alias in aliases:
                index_items.append(IndexItem(item=item, string=alias))

        self.setIndexItems(index_items)
