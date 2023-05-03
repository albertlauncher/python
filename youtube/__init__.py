import json
import re
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from albert import Action, Item, TriggerQuery, TriggerQueryHandler, critical, info, openUrl  # pylint: disable=import-error


md_iid = '1.0'
md_version = '1.4'
md_name = 'YouTube'
md_description = 'Query and open YouTube videos and channels'
md_url = 'https://github.com/albertlauncher/python/'
md_maintainers = '@stevenxxiu'

ICON_PATH = str(Path(__file__).parent / 'youtube.svg')
DATA_REGEX = re.compile(r'\b(var\s|window\[")ytInitialData("\])?\s*=\s*(.*)\s*;</script>', re.MULTILINE)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    )
}


def log_html(html: bytes) -> None:
    log_time = time.strftime('%Y%m%d-%H%M%S')
    log_name = 'albert.plugins.youtube_dump'
    log_path = Path(f'/tmp/{log_name}-{log_time}.html')

    with log_path.open('wb') as sr:
        sr.write(html)

    critical(f'The HTML output has been dumped to {log_path}')
    critical('If the page looks ok in a browser, please include the dump in a new issue:')
    critical('  https://www.github.com/albertlauncher/albert/issues/new')


def urlopen_with_headers(url: str) -> Any:
    req = Request(headers=HEADERS, url=url)
    return urlopen(req)


def text_from(val: dict[str, Any]) -> str:
    text = val['simpleText'] if 'runs' not in val else ''.join(str(v['text']) for v in val['runs'])

    return text.strip()


def download_item_icon(item: Item, temp_dir: Path) -> None:
    url = item.icon[0]
    video_id = url.split('/')[-2]
    path = temp_dir / f'{video_id}.png'
    with urlopen_with_headers(url) as response, path.open('wb') as sr:
        sr.write(response.read())
    item.icon = [str(path)]


def entry_to_item(type_, data) -> Item | None:
    icon = ICON_PATH
    match type_:
        case 'videoRenderer':
            subtext = ['Video']
            action = 'Watch on Youtube'
            url_path = f'watch?v={data["videoId"]}'
            if 'lengthText' in data:
                subtext.append(text_from(data['lengthText']))
            if 'shortViewCountText' in data:
                subtext.append(text_from(data['shortViewCountText']))
            if 'publishedTimeText' in data:
                subtext.append(text_from(data['publishedTimeText']))
            if data['thumbnail']['thumbnails']:
                icon = data['thumbnail']['thumbnails'][0]['url'].split('?', 1)[0]
        case 'channelRenderer':
            subtext = ['Channel']
            action = 'Show on Youtube'
            url_path = f'channel/{data["channelId"]}'
            if 'videoCountText' in data:
                subtext.append(text_from(data['videoCountText']))
            if 'subscriberCountText' in data:
                subtext.append(text_from(data['subscriberCountText']))
        case _:
            return None

    return Item(
        id=f'{md_name}/{url_path}',
        text=text_from(data['title']),
        subtext=' | '.join(subtext),
        icon=[icon],
        actions=[Action(f'{md_name}/{url_path}', action, lambda: openUrl(f'https://www.youtube.com/{url_path}'))],
    )


def results_to_items(results: dict) -> list[Item]:
    items: list[Item] = []
    for result in results:
        for type_, data in result.items():
            try:
                item = entry_to_item(type_, data)
                if item is None:
                    continue
                items.append(item)
            except KeyError as e:
                critical(e)
                critical(json.dumps(result, indent=4))
    return items


class Plugin(TriggerQueryHandler):
    temp_dir = None

    def id(self) -> str:
        return __name__

    def name(self) -> str:
        return md_name

    def description(self) -> str:
        return md_description

    def initialize(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix='albert_yt_'))

    def finalize(self) -> None:
        for child in self.temp_dir.iterdir():
            child.unlink()
        self.temp_dir.rmdir()

    def defaultTrigger(self) -> str:
        return 'yt '

    def synopsis(self) -> str:
        return 'query'

    def handleTriggerQuery(self, query: TriggerQuery) -> None:
        query_str = query.string.strip()
        if not query_str:
            return

        # Avoid rate limiting
        for _ in range(50):
            time.sleep(0.01)
            if not query.isValid:
                return

        info(f'Searching YouTube for \'{query_str}\'')
        url = f'https://www.youtube.com/results?{urlencode({"search_query": query_str})}'

        with urlopen_with_headers(url) as response:
            response_bytes: bytes = response.read()
            match = re.search(DATA_REGEX, response_bytes.decode())
            if match is None:
                critical(
                    'Failed to receive expected data from YouTube. This likely means API changes, but could just be a '
                    'failed request.'
                )
                log_html(response_bytes)
                return

            results = json.loads(match.group(3))
            primary_contents = results['contents']['twoColumnSearchResultsRenderer']['primaryContents']
            results = primary_contents['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
            items = results_to_items(results)

            # Purge previous icons
            for child in self.temp_dir.iterdir():
                child.unlink()

            # Download icons
            with ThreadPoolExecutor(max_workers=10) as e:
                for item in items:
                    e.submit(download_item_icon, item, self.temp_dir)
                    if not query.isValid:
                        return

            for item in items:
                query.add(item)

            # Add a link to the *YouTube* page, in case there's more results, including results we didn't include
            item = Item(
                id=f'{md_name}/show_more',
                text='Show more in browser',
                icon=[ICON_PATH],
                actions=[
                    Action(
                        f'{md_name}/show_more',
                        'Show more in browser',
                        lambda: openUrl(f'https://www.youtube.com/results?search_query={query_str}'),
                    )
                ],
            )
            query.add(item)
