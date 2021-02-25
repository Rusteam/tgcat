"""
Run inference on files
"""
from pathlib import Path
import os
import torch
import json
from tqdm import tqdm
import fasttext
import re
# custom
from src.train.text_utils import tokenize_text, lang_lemmatizer, preprocess_text

os.environ['KMP_DUPLICATE_LIB_OK']='True'

TGCAT_FILES = {
        'ru': 'models/trained/tgcat/ru_tgcat.pt',
        'en': 'models/trained/tgcat/en_tgcat.pt',
    }
TARGET_LANGS = list(TGCAT_FILES.keys())
LANG_DETECTION_MODEL = './models/external/lid.176.bin'

INPUT_FILE = "data/external/dc0206-input.txt"

def load_test_file(filepath):
    with open(filepath) as f:
        test_data = f.read().split('\n')
    test_data = list(filter(lambda x: x != '', test_data))
    test_data = list(map(lambda x: json.loads(x), test_data))
    print('Loaded', len(test_data), 'rows')
    return test_data


def format_text(channel):
    """ format text for running language detection """
    formatted = '\n'.join([channel['description'], '\n'.join(channel['recent_posts'])]).strip().replace('\n',' ')
    formatted = preprocess_text(formatted)
    return formatted


def is_kz_lang(text):
    ''' Returns True if text contains kz or uz chars '''
    kz_chars = "[ЎўҒғҲҳҚқ]"
    return re.search(kz_chars, text) is not None


lang_detector = fasttext.load_model(LANG_DETECTION_MODEL)
def predict_language(channel):
    formatted_text = format_text(channel)
    predicted = lang_detector.predict(formatted_text)
    lang_code = predicted[0][0].replace('__label__', '')
    if lang_code == 'ru' and is_kz_lang(formatted_text):
        lang_code = 'kz'
    return lang_code


def prepare_texts(channel_data, lang):
    """
    convert channel data to tokenized texts
    and return raw texts and tokens
     """
    raw = list(map(lambda x: '\n'.join(x['recent_posts'] + [x['title'], x['description']]), channel_data))
    # if lang == 'ru':
    #     tokenizer = lang_lemmatizer(lang)
    # else:
    tokenizer = tokenize_text
    tokens = list(map(lambda x: tokenizer(x), raw))
    return raw, tokens


def load_models():
    """ load tgcat models """
    tgcat = {l: torch.jit.load(f) for l, f in TGCAT_FILES.items()}
    return tgcat


tgcat = load_models()
def predict_topics(channel_data, lang_code):
    _, tokens = prepare_texts([channel_data], lang_code)
    top_predictions = tgcat[lang_code](tokens)[0]
    top_predictions = {k: round(v, 2) for k, v in top_predictions.items()}
    return top_predictions
    

if __name__ == '__main__':
    # load models and data
    test_data = load_test_file(INPUT_FILE)
    outputs = []
    ref_data = []
    # predict languages
    for data in tqdm(test_data, desc='channels'):
        lang_code = predict_language(data)
        is_target_lang = lang_code in TARGET_LANGS
        if is_target_lang:
            top_predictions = predict_topics(data, lang_code)
            data.update({
                'lang_code': lang_code,
                'category': top_predictions,
            })
            ref_data.append(data)
        else:
            top_predictions = {}
        outputs.append(str({
            'lang_code': lang_code if is_target_lang else 'other',
            'category': top_predictions
        }))
    # save predictions
    fname = Path(INPUT_FILE).stem
    with open(f'./data/processed/{fname}.txt', 'w') as f:
        f.write('\n'.join(outputs),)
    # save ref data
    with open(f'./data/processed/{fname}_reference.json', 'w') as f:
        json.dump(ref_data, f, indent=4, sort_keys=False)