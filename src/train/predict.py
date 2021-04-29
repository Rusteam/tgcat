"""
Run inference on files
"""
from pathlib import Path
import os, sys
import torch
import json
from tqdm import tqdm
import fasttext
import re
# custom
from src.train.text_utils import tokenize_text, preprocess_text

os.environ['KMP_DUPLICATE_LIB_OK']='True'

TGCAT_FILES = {
        'ru': 'models/trained/tgcat/ru_tgcat.pt',
        'en': 'models/trained/tgcat/en_tgcat.pt',
        'ar': 'models/trained/tgcat/ar_tgcat.pt',
        'fa': 'models/trained/tgcat/fa_tgcat.pt',
        'uz': 'models/trained/tgcat/uz_tgcat.pt',
    }
TARGET_LANGS = list(TGCAT_FILES.keys())
LANG_DETECTION_MODEL = './models/external/lid.176.bin'

assert len(sys.argv) > 1, "Provide input file path as `predict.py path/to/file.txt`"
INPUT_FILE = sys.argv[1]
assert os.path.exists(INPUT_FILE), f"{INPUT_FILE} does not exist"

def load_test_file(filepath, verbose=True):
    with open(filepath) as f:
        test_data = f.read().split('\n')
    test_data = list(filter(lambda x: x != '', test_data))
    test_data = list(map(lambda x: json.loads(x), test_data))
    if verbose:
        print('Loaded', len(test_data), 'rows')
    return test_data


def format_text(channel):
    """ format text for running language detection """
    formatted = prepare_text(channel)
    formatted = re.sub("\n", " ", formatted)
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


def prepare_text(row):
    """ extract and merge all text from a channel """
    post_texts = '\n'.join([
        post.get('text', "")
        if isinstance(post, dict) else post
        for post in row['recent_posts']
    ])
    merged = '\n'.join([row['title'], row['description'], post_texts])
    return merged


def load_models():
    """ load tgcat models """
    tgcat = {l: torch.jit.load(f) for l, f in TGCAT_FILES.items()}
    return tgcat


tgcat = load_models()
def predict_topics(channel_data, lang_code):
    tokens = prepare_text(channel_data)
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