# coding: utf-8
'''
Download news posts from Telegram public channels 

Config params:
      message_limit: max number of message from a channel
      languages: list of languages
      categories: list of categories
      telegram_channels_file: table with telegram channels data
'''
import asyncio
import  os
import pandas as pd
from tqdm import tqdm
from telethon import TelegramClient, functions, errors
from dotenv import load_dotenv
# custom imports
from src.train import PROJECT_DIR


load_dotenv()
# define variables to be used
SESSION_FILE = str(PROJECT_DIR / 'src/train/tg_sess')
envs = {k:os.environ[k] for k in ['TELEGRAM_APP_HASH', 'TELEGRAM_APP_ID']}

# file with telegram channels
CHANNELS_LIST_FILE = PROJECT_DIR / 'data/external/telegram_channels.csv'
CHANNEL_MESSAGE_LIMIT = 10

POSTS = 'data/raw/r-2/downloads/posts.csv'
META = 'data/raw/r-2/downloads/meta.csv'


def load_channels(channels_list_file):
    '''
    Load list of telegram channels to download posts from
    '''
    assert channels_list_file.exists(), f"{CHANNELS_LIST_FILE} does not exist"
    tg_channels = pd.read_csv(channels_list_file)
    tg_channels['username'] = tg_channels['link'].apply(lambda x: x.split('/')[-1])
    print(f"{len(tg_channels)} channels loaded")
    return tg_channels


async def download_channel_messages(client, channel_usernames, message_limit=CHANNEL_MESSAGE_LIMIT):
    '''
    Download messages from Telegram channels
    '''
    posts = list()
    for username in tqdm(channel_usernames, desc='channels'):
        try:
            messages = await client.get_messages(username, limit=message_limit)
            messages = [(username, msg.id, msg.date, msg.message,) for msg in messages]
            posts.extend(messages)
        except Exception as e:
            print(username, e)
    posts = pd.DataFrame(posts, columns=['channel', 'idx', 'date','message'])
    print(f"Downloaded {len(posts)} posts with limit {CHANNEL_MESSAGE_LIMIT} interval")
    return posts


async def extract_channel_meta(client, channel_usernames):
    """ get title and description of each channel """
    meta = []
    for username in tqdm(channel_usernames, desc='extracting meta-data'):
        try:
            chan = await client(functions.channels.GetFullChannelRequest(username))
            meta.append((username, chan.chats[0].title, chan.full_chat.about))
        except Exception as e:
            print(username, e)
    print(f"Extracted {len(meta)} meta-data for channels")
    meta = pd.DataFrame(meta, columns=['username', 'title','about'])
    return meta


def format_text_data(message_data, channel_data,
                    channel_meta_fields=['language',]):
    '''
    Merge messages and channel data to save as csv
    '''
    meta = channel_data.groupby('username')[channel_meta_fields].agg('first').to_dict()
    for tag in channel_meta_fields:
        message_data[tag] = message_data['channel'].apply(lambda x: meta[tag][x])
    if 'language' in channel_meta_fields:
        message_data['language'] = message_data['language'].apply(lambda x: x.lower()[:2])
    return message_data


def save_dataframe(posts, file, silent=True):
    """ save dataframe, if file exists append to it """
    if os.path.exists(file):
        posts.to_csv(file, index=False, headers=None, mode='a')
    else:
        posts.to_csv(file, index=False,)


async def download_posts():
    '''
    Run post download pipeline
    '''
    # load channels
    target_channels = load_channels(CHANNELS_LIST_FILE)
    channel_names = list(target_channels['username'].unique())
    # test telegram connection
    async with tg_client:
        me = await tg_client.get_me()
    print(f'Logged in as {me.username}')
    await tg_client.connect()
    # download message from channels
    # channel_entities = await get_channel_entities(tg_client, channel_names)
    meta = await extract_channel_meta(tg_client, channel_names)
    messages = await download_channel_messages(tg_client, channel_names,)
    data = format_text_data(messages, target_channels)
    await tg_client.disconnect()
    return data, meta


if __name__ == '__main__':
    tg_client = TelegramClient(SESSION_FILE, envs['TELEGRAM_APP_ID'], envs['TELEGRAM_APP_HASH'])
    with tg_client:
        posts,meta = tg_client.loop.run_until_complete(download_posts())
        # res = tg_client.loop.run_until_complete(download_channel_messages(tg_client, ['redakciya_channel', 'thingsprogrammersdo']))
    posts.to_csv(POSTS, index=False)
    meta.to_csv(META, index=False)
