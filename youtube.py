# -*- coding: utf-8 -*-

"""Query and open YouTube videos and channels.

Synopsis: <trigger> <query>"""

import json
import re
import time
from os import path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from albertv0 import Item, UrlAction, iconLookup

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'Youtube'
__version__ = '1.0'
__trigger__ = 'yt '
__author__ = 'Manuel Schneider'
__icon__ = iconLookup('youtube')  # path.dirname(__file__) + '/icons/YouTube.png'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/62.0.3202.62 Safari/537.36'
    )
}

re_videos = re.compile(r"^\s*window\[\"ytInitialData\"\] = (.*);$", re.MULTILINE)

def handleQuery(query):
    if query.isTriggered and query.string.strip():

        # avoid rate limiting
        time.sleep(0.2)
        if not query.isValid:
            return

        url_values = urlencode({'search_query': query.string.strip()})
        url = 'https://www.youtube.com/results?%s' % url_values
        req = Request(url=url, headers=HEADERS)
        with urlopen(req) as response:
            match = re.search(re_videos, response.read().decode())
            if match:
                results = json.loads(match.group(1))
                results = results['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                items = []
                for result in results:
                    for type, data in result.items():
                        try:
                            if type == 'videoRenderer':
                                id = data['videoId']
                                subtext = 'Video'
                                if 'lengthText' in data:
                                    subtext = subtext + " | %s" % data['lengthText']['simpleText'].strip()
                                if 'shortViewCountText' in data:
                                    subtext = subtext + " | %s" % data['shortViewCountText']['simpleText'].strip()
                                if 'publishedTimeText' in data:
                                    subtext = subtext + " | %s" % data['publishedTimeText']['simpleText'].strip()
                                actions=[ UrlAction('Watch on Youtube', 'https://youtube.com/watch?v=%s' % id) ]
                            elif type == 'channelRenderer':
                                id = data['channelId']
                                subtext = 'Channel'
                                if 'videoCountText' in data:
                                    subtext = subtext + " | %s" % data['videoCountText']['simpleText'].strip()
                                if 'subscriberCountText' in data:
                                    subtext = subtext + " | %s" % data['subscriberCountText']['simpleText'].strip()
                                actions=[ UrlAction('Show on Youtube', 'https://www.youtube.com/channel/%s' % id) ]
                            else:
                                continue
                        except Exception as e:
                            critical(e)
                            critical(json.dumps(result, indent=4))

                        item = Item(id=__prettyname__,
                                    icon=data['thumbnail']['thumbnails'][0]['url'].split('?', 1)[0] if data['thumbnail']['thumbnails'] else __icon__,
                                    text=data['title']['simpleText'],
                                    subtext=subtext,
                                    completion=query.rawString,
                                    actions=actions
                                )
                        items.append(item)
                return items
