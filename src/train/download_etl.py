import json
import os
import random
import time
from urllib.parse import urljoin
import logging

import bonobo
from bonobo.config import use_context_processor
from bonobo.constants import NOT_MODIFIED
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.train import PROJECT_DIR
from src.train.download import load_channels
from src.train.predict import load_test_file


CHANNELS_LIST_FILE = PROJECT_DIR / 'data/external/telegram_channels.csv'
OUTPUT_FILE = PROJECT_DIR / 'data/raw/r-2/downloads/channels.txt'


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
]


def get_channel_details(username):
    """ get channel title, description and recent posts"""
    # make a request
    username = username.split('/')[-1]
    url = urljoin('https://t.me/s/', username)
    resp = requests.get(url, headers={"User-Agent": random.choice(USER_AGENTS)})
    resp.raise_for_status()
    # parse html
    page = BeautifulSoup(resp.content.decode(), 'html.parser')
    channel_details = dict(
        title = "",
        description = "",
        recent_posts = [],
    )
    title_div = page.find('meta', property='og:title')
    if title_div is not None:
        channel_details['title'] = title_div.get('content').strip()
    description_div = page.find('meta', property='og:description')
    if description_div is not None:
        channel_details['description'] = description_div.get('content').replace('\t', '\n').strip()
    post_divs = page.find_all('div', "tgme_widget_message_wrap")
    post_divs = list(map(lambda x: x.findChild('div', 'tgme_widget_message_text'), post_divs))
    channel_details['recent_posts'] = [p.get_text('\n', strip=True) for p in post_divs if p is not None]
    return channel_details


def update_dict(src_dict,dest_dict):
    src_dict.update(dest_dict)
    return src_dict


SKIP = 'Telegram – a new era of messaging'
def extract():
    if os.path.exists(OUTPUT_FILE):
        exclude = pd.DataFrame(load_test_file(OUTPUT_FILE))
        already_downloaded = exclude['username'].tolist()
    else:
        already_downloaded = []
    channels = load_channels(CHANNELS_LIST_FILE, exclude=already_downloaded)
    for i,row in channels.iterrows():
        try:
            details = get_channel_details(row['username'])
            meta = row[['username', 'language', 'topic [Primary]', 'topic [Secondary]']].to_dict()
            if details['title'] != SKIP:
                yield [meta, details]
        except Exception as e:
            logging.error(e)


def transform(*args):
    # for row in rows:
    meta,texts = args
    new = update_dict(meta, texts)
    return new


if __name__ == '__main__':
    channels = extract()
    i = 0
    with open(OUTPUT_FILE, 'a+') as f:
        for chan in tqdm(channels, desc='channels'):
            transformed = transform(*chan)
            f.write(json.dumps(transformed, ensure_ascii=False) + '\n')
            time.sleep(random.randint(0, 2))
            i += 1
            # if i > 3:
            #     break