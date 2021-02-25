"""
build a streamlit app to make predictions of user-provided links
"""
import html
import random
import re
from urllib.parse import urljoin

import altair as alt
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import torch.jit
from bs4 import BeautifulSoup
from pyonmttok._ext import Tokenizer

# custom
from src.train.predict import TGCAT_FILES, predict_language, predict_topics

# TODO localize topic names
# TODO get channel counters


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
        "en": "Recent posts",
        "ru": "Последние посты"
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
    "success": {
        "en": "Finished querying data and making predictions!",
        "ru": "Загрузка данных и определение тематики завершены"
    },
    "about_title": {
        "en": "About us",
        "ru": "Немного о нас"
    },
    "about": {
        "en": [
            """
            We have developed these algorithms as part of 
            [Telegram data clustering contest](https://contest.com/docs/dc2021-r1).
            
            This time, however, we have decided against just archiving our code and models somewhere on GitHub
            and let people use these machine learning models.
            """,
            """
            **Out team:**
            - [Rustem Galileo, applied data scientist](https://rusteam.github.io/)
            - [Almaz Melnikov, machine learning engineer](https://www.linkedin.com/in/almazmelnikov/)
            """
        ],
        "ru": [
            """
            Алгоритмы разработаны в рамках 
            [конкурса по кластеризации данных от Телеграм](https://contest.com/docs/dc2021-r1/ru).
            
            Однако на этот раз мы решили не архивировать наш код и построенные модели где-нибудь на гитхабе,
            а дать возможность миру пользоваться нашей разработкой.
            """,
            """
            **Наша команда:**
            - [Г. Рустем, дата саентист](https://rusteam.github.io/)
            - [М. Алмаз, инженер-исследователь](https://www.linkedin.com/in/almazmelnikov/)
            """
        ],
    }
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
    },
    "nothing_selected": {
        "en": "Select topics of interest to see similar channels",
        "ru": "Выберите интересующие вас темы, чтобы отобразить схожие каналы"
    },
    "no_posts": {
        'en': "Unable to fetch messages",
        "ru": "Отсутствует доступ к сообщениям из канала"
    }
}
REF_FILES = [
    'data/processed/dc0212-input_reference.json',
    "data/processed/dc0206-input_reference.json",
]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
]



@st.cache(suppress_st_warning=True)
def load_channels():
    # load channels with topics
    data = pd.concat([pd.read_json(f) for f in REF_FILES])
    data['topics'] = data['category'].apply(lambda x: list(x.keys()))
    return data


@st.cache()
def filter_channels(selected_topics, lang):
    is_match = channels['topics'].apply(lambda x: len(set(selected_topics).intersection(x)) > 0)
    is_lang = channels['lang_code'] == lang
    return channels.copy().loc[is_match & is_lang].reset_index(drop=True)


@st.cache(hash_funcs={
    torch.jit._script.RecursiveScriptModule: id,
    Tokenizer: id,
})
def get_channel_topics(channel_details):
    """ get language and topic predictions on change of channel details """
    channel_lang = predict_language(channel_details)
    if channel_lang in LANGS:
        predictions = predict_topics(channel_details, channel_lang)
    else:
        predictions = {}
    # predictions = pd.DataFrame(predictions, index=[0])
    return channel_lang, predictions


def extract_username(username):
    """ check if username is link or @username """
    match = re.match("(https://t\.me/|@)([a-z_0-9]{5,32})$", username.strip(), flags=re.IGNORECASE)
    return None if match is None else match.group(2)


@st.cache()
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


def limit_post(post_message, max_len=300):
    """ if post len too long, then cut it"""
    if len(post_message) < max_len:
        return post_message
    else:
        return post_message[:max_len] + '...'


@st.cache
def create_js_swiper(texts):
    """ create vertical SwiperJS to be rendered """
    dom = '\n'.join([
        """
        <head>
            <link rel="stylesheet" href="https://unpkg.com/swiper/swiper-bundle.min.css">
            <style>
                html,
                body {
                  position: relative;
                  height: 100%;
                }
            
                 body {
                  font-family: Helvetica Neue, Helvetica, Arial, sans-serif;
                  font-size: 14px;
                  color: #000;
                  margin: 0;
                  padding: 0;
                }
            
                .swiper-container {
                  width: 100%;
                  height: 100%;
                }
            
                .swiper-slide {
                  width: 95%; 
                  text-align: center;
                  font-size: 1rem;
                  font-weight: 400;
                  font-family: IBM Plex Sans, sans-serif;
                  background: #fff;
            
                  /* Center slide text vertically */
                  display: -webkit-box;
                  display: -ms-flexbox;
                  display: -webkit-flex;
                  display: flex;
                  -webkit-box-pack: center;
                  -ms-flex-pack: center;
                  -webkit-justify-content: center;
                  justify-content: center;
                  -webkit-box-align: center;
                  -ms-flex-align: center;
                  -webkit-align-items: center;
                  align-items: center;
                }
            </style>
        </head>
        <body>
            <div class="swiper-container">
                <div class="swiper-wrapper">
        """,
        "\n".join([f'<div class="swiper-slide">{html.escape(limit_post(t))}</div>' for t in texts]),
        """
                </div>
                <div class="swiper-pagination"></div>
            </div>
            <!-- Swiper JS -->
            <script src="https://unpkg.com/swiper/swiper-bundle.min.js"></script>
            <!-- Init swiper -->
            <script>
            var swiper = new Swiper('.swiper-container', {
              direction: 'vertical',
              pagination: {
                el: '.swiper-pagination',
                clickable: true,
              },
            });
            </script>
        </body>
        """
        ])
    return dom

def create_barplot(predictions):
    data = pd.DataFrame([{'topic': k, 'weight': v} for k,v in predictions.items()], )
    chart = alt.Chart(data).mark_bar().encode(x='weight', y='topic', color='topic')
    return chart


channels = load_channels()


def main():
    """ create a page layout """
    # select language
    _,header_right = st.beta_columns((9,1))
    with header_right:
        lang = st.selectbox("", options=LANGS,)

    # about
    st.sidebar.title(TEXTS['about_title'][lang])
    for txt in TEXTS['about'][lang]:
        st.sidebar.markdown(txt)

    # intro
    st.title(TEXTS['title'][lang])
    st.text(TEXTS['description'][lang])
    with st.beta_expander(TEXTS['instruction_expander'][lang], expanded=False):
        st.markdown(TEXTS['instructions'][lang])
    st.markdown("---")

    # channel input and predictions
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
            # channel_details = asyncio.run(get_channel_details(username), debug=True)
            channel_details = get_channel_details(username)
        except Exception as e:
            print(e)
            st.error(ERRORS['channel_invalid'][lang].format(username=username))
            return
    with st.spinner(TEXTS['spinner_predictions'][lang]):
        channel_lang, predictions = get_channel_topics(channel_details)
        if channel_lang not in LANGS:
            st.error(ERRORS['lang_code'][lang])
            return
        else:
            st.success(TEXTS['success'][lang])

    # Output
    st.subheader(TEXTS['output_header'][lang])
    main_left,main_right = st.beta_columns(2)
    with main_left:
        st.text(TEXTS['channel_subheader'][lang])
        st.write(f"**{TEXTS['channel_title'][lang]}:** {channel_details['title']}")
        st.write(f"**{TEXTS['channel_description'][lang]}:** {channel_details['description']}")
    with main_right:
        st.text(TEXTS['recent_posts'][lang])
        if len(channel_details['recent_posts']):
            swiper = create_js_swiper(channel_details['recent_posts'])
            components.html(swiper, height=200)
        else:
            st.warning(ERRORS['no_posts'][lang])

    st.text('\n')
    st.text(TEXTS['predictions_subheader'][lang])

    barplot = create_barplot(predictions)
    st.altair_chart(barplot, use_container_width=True)

    # More channels with the same topic
    st.markdown('---')
    st.subheader(TEXTS['similar_channels'][lang])
    more_topics = st.multiselect(TEXTS['select_topics'][lang], list(predictions.keys()),)
    similar_channels = filter_channels(more_topics, channel_lang)
    if len(similar_channels) > 0:
        st.table(similar_channels[['title','description','category']].sample(min(10, len(similar_channels))).reset_index(drop=True))
    else:
        st.warning(ERRORS['nothing_selected'][lang])


if __name__ == '__main__':
    main()