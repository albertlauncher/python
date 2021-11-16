# -*- coding: utf-8 -*-

"""Query and open YouTube videos and channels.

Synopsis: <trigger> <query>"""

import json
import re
import time
from os import path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from albert import Item, UrlAction, iconLookup, critical, debug, info

__title__ = 'Youtube'
__version__ = '0.4.1'
__triggers__ = 'yt '
__authors__ = "Manuel S."
__icon__ = iconLookup('youtube')  # path.dirname(__file__) + '/icons/YouTube.png'

DATA_REGEX = re.compile(r'^\s*(var\s|window\[")ytInitialData("\])?\s*=\s*(.*)\s*;\s*$', re.MULTILINE)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/62.0.3202.62 Safari/537.36'
    )
}

def handleQuery(query):
    if query.isTriggered and query.string.strip():

        # avoid rate limiting
        time.sleep(0.2)
        if not query.isValid:
            return

        info("Searching YouTube for '{}'".format(query.string))
        req = Request(headers=HEADERS, url='https://www.youtube.com/results?{}'.format(
            urlencode({ 'search_query': query.string.strip() })))

        with urlopen(req) as response:
            responseBytes = response.read()
            match = re.search(DATA_REGEX, responseBytes.decode())
            if match is None:
                critical("Failed to receive expected data from YouTube. This likely means API changes, but could just be a failed request.")
                logHtml(responseBytes)
                return

            results = json.loads(match.group(3))
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

                    item = Item(id=__title__,
                                icon=data['thumbnail']['thumbnails'][0]['url'].split('?', 1)[0] if data['thumbnail']['thumbnails'] else __icon__,
                                text=textFrom(data['title']),
                                subtext=' | '.join(subtext),
                                actions=[ UrlAction(action, 'https://www.youtube.com/' + link) ]
                            )
                    items.append(item)
            return items

def textFrom(val):
    text = val['simpleText'] if 'runs' not in val else \
        ''.join('{}'.format(v['text']) for v in val['runs'])

    return text.strip()

def logHtml(html):
    logTime = time.strftime("%Y%m%d-%H%M%S")
    logName = 'albert.plugins.youtube_dump'
    logPath = '/tmp/{}-{}.html'.format(logName, logTime)

    f = open(logPath, 'wb')
    f.write(html)
    f.close()

    critical("The HTML output has been dumped to {}.".format(logPath))
    critical("If the page looks ok in a browser, please include the dump in a new issue:")
    critical("  https://www.github.com/albertlauncher/albert/issues/new")
