"""
build a streamlit app to make predictions of user-provided links
"""

import streamlit as st
import pandas as pd
import json
import random
import torch.jit
import re
import asyncio
from telethon import functions, tl, TelegramClient
# custom
from src.train.predict import TGCAT_FILES, predict_language, predict_topics
from src.train.download import SESSION_FILE, envs as tg_env

# TODO configure how many top topics to see and how many recent posts
# TODO add about us
# TODO use test data as a reference
# TODO handle session keys for multi-threaded

LANGS = list(TGCAT_FILES.keys())
TEXTS = {
    "title": {
        'en': "Topic classification for Telegram channels",
        "ru": "Распознавание тематики Телеграм-каналов",
    },
    "description": {
        "en": "Use machine learning to classify what Telegram channels are talking about",
        "ru": "Определение тематики постов на основе обученных машинных алгоритмов",
    },
    "instruction_expander": {
        "en": "Very short intro",
        "ru": "Очень короткая инструкция"
    },
    "instructions": {
        "en": """
        1. Enter URL of a telegram channel (can be copied from a channel info)
        2. Review outputs: 
            - left: channel details such as title, description and recent posts
            - right: topic predictions for the channel
        3. Explore similar channels with similar topics
        """,
        "ru": """
        1. Вставьте ссылку на Телеграм-канал (можно скопировать со страницы канала)
        2. Отображение результатов ниже:
            - слева: информация о канале и последние посты
            - справа: результаты работы алгоритма по распознаванию тематик
        3. Найти схожие каналы
        """,
    },
    "main_header": {
        "en": "Identify channel topics",
        "ru": "Определить тематику канала"
    },
    "input_text": {
        "en": "https://t.me/username or @username",
        "ru": "https://t.me/username или @username"
    },
    "input_header": {
        'en': "Enter URL of a Telegram channel",
        "ru": "Введите ссылку на Телеграм-канал"
    },
    "output_header": {
        'en': "Outputs",
        "ru": "Результаты"
    },
    "channel_subheader": {
            "en": "Channel details",
            "ru": "Информация о канале"
        },
    "predictions_subheader": {
        'en': "Predictions",
        'ru': "Результаты классфикации"
    },
    "channel_title": {
        "en": "title",
        "ru": "канал"
    },
    "channel_description": {
        "en": "description",
        "ru": "описание"
    },
    "recent_posts": {
        "en": "recent posts",
        "ru": "последние посты"
    },
    "more_posts": {
        'en': "more posts",
        "ru": "показать больше"
    },
    'similar_channels': {
        'en': 'Explore similar channels',
        'ru': 'Найти схожие каналы'
    },
    "select_topics": {
        'en': 'Select 1 or more topics',
        'ru': "Выберите тематики"
    },
    "spinner_channel": {
        "en": "Querying Telegram for channel details",
        "ru": "Загружаем информацию о канале"
    },
    "spinner_predictions": {
        "en": "Running the model on downloaded data",
        "ru": "Прогоняем загруженные данные через модель"
    },
}
ERRORS = {
    "user_input": {
        "en": "Make sure your link is valid",
        "ru": "Проверьте правильность заполнения ссылки"
    },
    "lang_code": {
        "en": f"Language detected is not among {LANGS}",
        "ru": f"На данный момент распознаем только на следующих языках: {LANGS}"
    },
    "channel_invalid": {
        "en": "{username} is not a valid public channel",
        "ru": "не похоже, что {username} является открытым каналом"
    }
}


@st.cache()
def load_channels():
    # load channels with topics
    data = pd.read_csv('./data/external/telegram_channels.csv')
    data['topics'] = data['topic [Primary]'].apply(lambda x: x.split(','))
    data['username'] = data['link'].apply(lambda x: x.split('/')[-1])
    data['lang_code'] = data['language'].apply(lambda x: x.lower()[:2])
    # load titles and descriptions
    meta = pd.read_csv('./data/raw/meta.csv')
    meta.rename({'about': 'description'}, axis=1, inplace=True)
    data = data.merge(meta, how='inner', on='username')
    return data[['link', 'title', 'description', 'topics', 'lang_code']]


@st.cache()
def filter_channels(selected_topics, lang):
    is_match = channels['topics'].apply(lambda x: len(set(selected_topics).intersection(x)) > 0)
    is_lang = channels['lang_code'] == lang
    return channels.loc[is_match & is_lang].reset_index(drop=True)


@st.cache()
def load_random_channels():
    """ load labelling tasks to use them as placeholder """
    with open("data/processed/labelling_tasks_sample.json") as f:
        data = json.load(f)
    return data


# @st.cache(hash_funcs={
#     torch.jit._script.RecursiveScriptModule: lambda x: x,
# })
def get_channel_topics(channel_details):
    """ get language and topic predictions on change of channel details """
    channel_lang = predict_language(channel_details)
    if channel_lang in LANGS:
        predictions = predict_topics(channel_details, channel_lang)
    else:
        predictions = {}
    predictions = pd.DataFrame(predictions, index=[0])
    return channel_lang, predictions


# @st.cache(hash_funcs={asyncio.coroutine: lambda x: x})
async def create_tg_connection():
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    tg_client = TelegramClient(SESSION_FILE, tg_env['TELEGRAM_APP_ID'], tg_env['TELEGRAM_APP_HASH'])
    async with tg_client:
        me = await tg_client.get_me()
    print(f'Logged in as {me.username}')
    await tg_client.start()
    return tg_client


def extract_username(username):
    """ check if username is link or @username """
    match = re.match("(https://t\.me/|@)([a-z_0-9]{5,32})$", username.strip(), flags=re.IGNORECASE)
    return None if match is None else match.group(2)


async def get_channel_details(channel):
    # async with tg_client:
    tg_client = TelegramClient(SESSION_FILE, tg_env['TELEGRAM_APP_ID'], tg_env['TELEGRAM_APP_HASH'])
    channel_details = {'title': "", 'description': "", "recent_posts": []}
    async with tg_client:
        ent = await tg_client.get_entity(channel)
        assert isinstance(ent, tl.types.Channel)
        meta = await tg_client(functions.channels.GetFullChannelRequest(channel))
        posts = await tg_client.get_messages(channel, limit=10)
    channel_details.update({
        'title': meta.chats[0].title,
        'description': meta.full_chat.about
    })
    if len(posts) > 0:
        channel_details.update({'recent_posts': [p.message for p in posts if p.message is not None]})
    return channel_details


channels = load_channels()
random_channels = load_random_channels()
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# tg_client = asyncio.run(create_tg_connection(), debug=True)


def main():
    # select language
    _,header_right = st.beta_columns((9,1))
    with header_right:
        lang = st.selectbox("", options=LANGS,)

    # intro
    st.title(TEXTS['title'][lang])
    st.text(TEXTS['description'][lang])
    with st.beta_expander(TEXTS['instruction_expander'][lang], expanded=False):
        st.markdown(TEXTS['instructions'][lang])
    st.markdown("---")

    # channel input and predictions
    # st.header(TEXTS['main_header'][lang])
    st.subheader(TEXTS['input_header'][lang])
    username = st.text_input(TEXTS['input_text'][lang],)
    username = extract_username(username)
    st.markdown('---')
    if username is None:
        st.error(ERRORS['user_input'][lang])
        return

    # get predictions
    with st.spinner(TEXTS['spinner_channel'][lang]):
        try:
            channel_details = asyncio.run(get_channel_details(username))
        except Exception as e:
            st.error(ERRORS['channel_invalid'][lang].format(username=username))
            return
    with st.spinner(TEXTS['spinner_predictions'][lang]):
        channel_lang, predictions = get_channel_topics(channel_details)
    if channel_lang not in LANGS:
        st.error(ERRORS['lang_code'][lang])
        return

    # Output
    st.subheader(TEXTS['output_header'][lang])
    main_left,main_right = st.beta_columns(2)
    with main_left:
        st.text(TEXTS['channel_subheader'][lang])
        st.write(f"**{TEXTS['channel_title'][lang]}:** {channel_details['title']}")
        st.write(f"**{TEXTS['channel_description'][lang]}:** {channel_details['description']}")
        with st.beta_expander(TEXTS['recent_posts'][lang]):
            for post in channel_details['recent_posts']:
                st.text("- " + post)
                st.text('\n')
    with main_right:
        st.text(TEXTS['predictions_subheader'][lang])
        st.bar_chart(predictions, use_container_width=False)

    # More channels with the same topic
    st.markdown('---')
    st.subheader(TEXTS['similar_channels'][lang])
    more_topics = st.multiselect(TEXTS['select_topics'][lang], predictions.columns.values,)
    similar_channels = filter_channels(more_topics, channel_lang)
    if len(similar_channels) > 0:
        st.table(similar_channels[['link','title','description']])


if __name__ == '__main__':
    main()