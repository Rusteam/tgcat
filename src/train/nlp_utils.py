# coding: utf-8
'''
Helper functions to:
    - parse html files
    - clean text fields
    - write json output
'''
from pathlib import Path
import os, sys
import re
from collections import Counter
import glob
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import yaml
import pandas as pd
from pymystem3 import Mystem, constants
import spacy


def load_yaml(filepath):
    ''' Load yaml file with implied types (safe loader) '''
    with open(filepath, 'r') as f:
        content = yaml.load(f, yaml.SafeLoader)
    return content


def list_html_files(folder):
    ''' List html files that are inside the folder or in its subdirectories '''
    folder = Path(folder)
    return folder.glob('**/*.html')


def read_html(file):
    ''' Read and prettify html file with beautiful soup '''
    assert os.path.exists(file), f"{file} does not exist"
    with open(file, 'r', encoding='utf-8') as htmldoc:
        soup = bs(htmldoc, 'html.parser')
        soup.prettify()
    return soup


def extract_metadata(soup, meta_properties=['title','published_time',
                                            'description','site_name'],
                        silent=True):
    '''
    Extract meta features like title, datetime and description from a html soup
    If no content in a meta property, return None
    '''
    features = {}
    for prop in meta_properties:
        try:
            prefix = 'article' if prop == 'published_time' else 'og'
            meta = soup.find("meta",  property=f"{prefix}:{prop}").get('content')
            features[prop] = meta
        except AttributeError as e:
            if not silent:
                print(f'[ERROR] No content in {prop}')
    return features


def extract_text(soup):
    ''' Extract text contents from a html soup '''
    raw_text = []
    for tag in soup.find('article').find_all(True):
        if tag.name in ['p','h1','h2','h3','h4','a']:
            if tag.text=='Related Articles':
                continue
            raw_text.append(tag.text.strip('\n'))
    return '\n'.join(raw_text)


def check_for_args(index=1):
    ''' Make sure argument is provided '''
    try:
        arg = sys.argv[index]
    except IndexError as e:
        raise Exception(f"Provide an argument at index {index}")
    return arg


def do_paths_exist(*args):
    ''' Test if paths given exist '''
    assert len(args) > 0
    for path in args:
        assert os.path.exists(path), f"{path} does not exist"


def lemmatize_word(token, lang, lemmatizer):
    ''' Lemmatize a token either in english or russian '''
    assert lang in ['en','ru']
    if lang == 'en':
        normal_token = lemmatizer.lemmatize(token)
    else:
        normal_token = lemmatizer.parse(token)[0].normal_form
    return normal_token


def load_lemmatizers():
    """ Load english spacy and russian pymystem """
    global nlp
    # get mystem bin
    frozen_mode = hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS')
    if frozen_mode:
        mystem_bin = Path(__file__).resolve().parent.parent / 'models/shared/mystem'
        if not Path(mystem_bin).is_file():
            import tarfile
            tmp_path = Path(mystem_bin).parent / "mystem-3.0-linux3.1-64bit.tar.gz"
            tar = tarfile.open(tmp_path)
            try:
                tar.extract(Path(mystem_bin).name, Path(mystem_bin).parent)
            finally:
                tar.close()
    else:
        mystem_bin = None
    nlp = {
        'en': spacy.load('en', disable=['parser','ner']),
        'ru': Mystem(mystem_bin=mystem_bin),
        }


def is_valid_token(token):
    ''' Return True if token is not space or punct '''
    s = sum([token.is_punct, token.is_space])
    return s == 0


def spacy_en_tokens(text):
    ''' Get en tokens using spacy'''
    assert 'nlp' in globals()
    doc = nlp['en'](text)
    tokens = [{
        'word': token.text, 
        'lemma': token.lemma_.lower(),
        'pos': token.pos_,
         } 
        for token in doc
        if is_valid_token(token)
    ]
    return tokens


def get_tokens(text, lang):
    ''' 
    Return a list dictionaries as:
        {
            word: Original word, 
            lemma: lowercase lemma, 
            pos: part of speech given my lemmatizer
         }
    '''
    if lang == 'en':
        tokens = spacy_en_tokens(text)
    elif lang == 'ru':
        tokens = mystem_tokens(text)
    else:
        raise NotImplementedError
    return tokens


def extract_mystem_pos_tag(grammar_info):
    """ Extract pos tag from pymystem's full grammar info """
    tags = grammar_info.split('=')[0]
    pos = tags.split(',')[0]
    return pos


def mystem_tokens(raw_text):
    res = nlp['ru'].analyze(raw_text)
    res = [{
        'lemma': token['analysis'][0]['lex'],
        'pos': extract_mystem_pos_tag(token['analysis'][0]['gr']),
        'word': token['text']
    } for token in res if 'analysis' in token.keys() and 
                len(token['analysis']) > 0]
    return res


def select_lemmas(tokens, target_pos):
    ''' Select lemmas with lemmas within given pos tags '''
    return [t['lemma'] for t in tokens
            if t['pos'] in target_pos]


def count_pos_tags(tokens):
    ''' Return a counter of all pos tags '''
    c = Counter(t['pos'] for t in tokens)
    return dict(c)


def discard_url(url, extensions=['jpeg','jpg','pdf'], 
                domains=['https://t\.me/', 'twitter\.com','facebook\.com','instragram\.com']):
    '''
    Detect if url is image or video or social media post
    '''
    ext = url.split('.')[-1].lower()
    domains = '|'.join(domains)
    is_domain_match = re.search(domains, url) is not None
    return ext in extensions or is_domain_match