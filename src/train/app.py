"""
build a streamlit app to make predictions of user-provided links
"""

import streamlit as st
import pandas as pd
# custom
from src.train.predict import TGCAT_FILES

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
        "en": "Enter URL of a Telegram channel",
        "ru": "Введите ссылку на Телеграм-канал"
    },
    "input_header": {
        'en': "Inputs",
        "ru": "Ввод данных"
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
    }
}
channel_title = "Sports.ru"
channel_description = """
Лучшее приложение о спорте: trbna.co/SportsApp

Инстаграм: trbna.co/SportsInst
Facebook: trbna.co/SportsFB

📩 По вопросам рекламы в телеграм-каналах: @sportsru_ads_bot
"""
recent_posts = [
    """🔥 Итак, Мбаппе – новый король «Камп Ноу»! Французский форвард положил хет-трик на поле «Барсы» (первым после Шевченко) и обеспечил «ПСЖ» мощнейшие 4:1.

Давайте со свежей головой еще раз посмотрим голы и восхитимся величием Килиана👇
https://www.sports.ru/tribuna/blogs/mama4h/2889995.html?utm_source=telegram&utm_medium=dmi&utm_campaign=2021-02-17
""",
    """⚡️ МЕДВЕДЕВ В ПОЛУФИНАЛЕ AUSTRALIAN OPEN!

🇷🇺 Даниил обыграл в российском дерби Андрея Рублева в трех сетах и присоединился к Аслану Карацеву в четверке лучших первого турнира «Большого шлема» 2021 года!

@sportsru""",
    """👍 «Ливерпуль» победил «Лейпциг» в гостях (в Будапеште) и добыл комфортное преимущество в два мяча перед ответным матчем.

Забитцер выдал идеальный пас на ход Салаху, а Мукиеле вывел Мане один на один. Смотрим, как чудили футболисты немецкого клуба, а парни Клоппа хладнокровно этим воспользовались👇
https://www.sports.ru/tribuna/blogs/mama4h/2890004.html?utm_source=telegram&utm_medium=dmi&utm_campaign=2021-02-17

@sportsru""",
]
predictions = pd.DataFrame({
        "Culture & Events": 0.5,
        "Health & Medicine": 0.22,
        "Offers & Promotions": 0.15,
        "Video Games": 0.13}, index=[0])

@st.cache()
def load_channels():
    # load channels with topics
    data = pd.read_csv('./data/external/telegram_channels.csv')
    data['topics'] = data['topic [Primary]'].apply(lambda x: x.split(','))
    data['username'] = data['link'].apply(lambda x: x.split('/')[-1])
    # load titles and descriptions
    meta = pd.read_csv('./data/raw/meta.csv')
    meta.rename({'about': 'description'}, axis=1, inplace=True)
    data = data.merge(meta, how='inner', on='username')
    return data[['link', 'title', 'description', 'topics']]


@st.cache()
def filter_channels(selected_topics):
    is_match = channels['topics'].apply(lambda x: len(set(selected_topics).intersection(x)) > 0)
    return channels.loc[is_match].reset_index(drop=True)


channels = load_channels()

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
username = st.text_input(TEXTS['input_text'][lang], value="https://t.me/username")
st.markdown('---')

# Output
st.subheader(TEXTS['output_header'][lang])
main_left,main_right = st.beta_columns(2)
with main_left:
    st.text(TEXTS['channel_subheader'][lang])
    st.write(f"**{TEXTS['channel_title'][lang]}:** {channel_title}")
    st.write(f"**{TEXTS['channel_description'][lang]}:** {channel_description}")
    st.write(f"**{TEXTS['recent_posts'][lang]}**:")
    st.write(recent_posts[0])
    with st.beta_expander(TEXTS['more_posts'][lang]):
        for post in recent_posts[1:]:
            st.write(post)
with main_right:
    st.text(TEXTS['predictions_subheader'][lang])
    st.bar_chart(predictions, use_container_width=True)

# More channels with the same topic
st.markdown('---')
st.subheader(TEXTS['similar_channels'][lang])
more_topics = st.multiselect(TEXTS['select_topics'][lang], predictions.columns.values,)
similar_channels = filter_channels(more_topics)
st.table(similar_channels)