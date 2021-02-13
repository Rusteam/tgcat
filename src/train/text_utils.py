import re
import pyonmttok
from src.train.nlp_utils import load_lemmatizers, get_tokens, select_lemmas


def process_topics(topics):
    ''' remove empty ones and strip from whitespaces '''
    topics = list(filter(lambda x: x != '', 
                        topics))
    topics = list(map(lambda x: x.strip(), topics))
    return topics


def raw2list(raw):
    """convert raw str or dict field to a list of topics """
    if isinstance(raw, dict):
        raw = raw['choices']
    else:
        raw = [str(raw)]
    return raw


def get_test_topics(primary, secondary):
    """ merge primary and secondary """
    primary = raw2list(primary)
    if secondary != '':
        primary += raw2list(secondary)
    return primary


def prepare_inputs(channel_data, target_fields):
    """ receive one channel example and return its texts from title, description and posts """
    inputs = []
    if 'title' in target_fields:
        inputs.append(channel_data['title'])
    if 'description' in target_fields:
        inputs.append(channel_data['description'])
    if 'posts' in target_fields:
        inputs += list(channel_data['posts'])
    return '\n'.join(inputs)


def process_tokens(tokens):
    """filter out useless tokens as empty or non-words"""
    tokens = list(map(lambda x: re.sub('[\W\d]', '', x),
                     tokens))
    tokens = list(filter(lambda x: len(x) > 1,
                    tokens))
    return tokens


tokenizer = pyonmttok.Tokenizer('aggressive', joiner_annotate=True)


def preprocess_text(text):
    """remove url, non-words chars """
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
             " ", text)
    return text.lower()

def tokenize_text(text):
    """ split into lowercase tokens """
    text = preprocess_text(text)
    tokens,_ = tokenizer.tokenize(text)
    tokens = process_tokens(tokens)
    return tokens


POS = {
    "en": ['NOUN', 'PROPN', 'ADJ', 'VERB'],
    "ru": ['A', 'S',]
}

load_lemmatizers()


def lang_lemmatizer(language):
    def lemmatize_text(text):
        """ get lemmas and POS tags, select target POS lemmas and filter trash """
        text = preprocess_text(text)
        tokens = get_tokens(text, language)
        lemmas = select_lemmas(tokens, POS[language])
        lemmas = process_tokens(lemmas)
        return lemmas
    return lemmatize_text
