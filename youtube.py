# -*- coding: utf-8 -*-

"""Query and open YouTube videos and channels.

Synopsis: <trigger> <query>"""

import json
import re
import time
from os import path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from albertv0 import Item, UrlAction, iconLookup, critical

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'Youtube'
__version__ = '1.1'
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

        req = Request(headers=HEADERS, url='https://www.youtube.com/results?{}'.format(
            urlencode({ 'search_query': query.string.strip() })))

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
                                subtext = ['Video']
                                action = 'Watch on Youtube'
                                link = 'watch?v={}'.format(data['videoId'])

                                if 'lengthText' in data:
                                    subtext.append(textFrom(data['lengthText']))
                                if 'shortViewCountText' in data:
                                    subtext.append(textFrom(data['shortViewCountText']))
                                if 'publishedTimeText' in data:
                                    subtext.append(textFrom(data['publishedTimeText']))

                            elif type == 'channelRenderer':
                                subtext = ['Channel']
                                action = 'Show on Youtube'
                                link = 'channel/{}'.format(data['channelId'])

                                if 'videoCountText' in data:
                                    subtext.append(textFrom(data['videoCountText']))
                                if 'subscriberCountText' in data:
                                    subtext.append(textFrom(data['subscriberCountText']))
                            else:
                                continue
                        except Exception as e:
                            critical(e)
                            critical(json.dumps(result, indent=4))

                        item = Item(id=__prettyname__,
                                    icon=data['thumbnail']['thumbnails'][0]['url'].split('?', 1)[0] if data['thumbnail']['thumbnails'] else __icon__,
                                    text=textFrom(data['title']),
                                    subtext=' | '.join(subtext),
                                    completion=query.rawString,
                                    actions=[ UrlAction(action, 'https://www.youtube.com/' + link) ]
                                )
                        items.append(item)
                return items

def textFrom(val):
    text = val['simpleText'] if 'runs' not in val else \
        ''.join('{}'.format(v['text']) for v in val['runs'])

    return text.strip()
