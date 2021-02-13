# coding: utf-8

# # Prepare test data for annotation

import os, sys
from pathlib import Path
from pprint import pprint
import random
import json
import itertools
from datetime import datetime as dt
# ds libs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import torch
# custom
from src.train.predict import prepare_texts, load_models, load_test_file, format_text, predict_language


# ## Load Data

FILES = [
    # 'data/external/dc0130-input.txt',
    # 'data/external/dc0202-input.txt',
    'data/external/dc0212-input.txt',
]
TARGET_LANGS = ['en', 'ru']
TRAIN_DATA = './data/interim/train_data.csv'
TOP_N = 1


# Load data
test_data = [load_test_file(f) for f in FILES]
test_data = sum(test_data, [])
print('Num examples', len(test_data))

# ## Detect target languages
target = []
for data in tqdm(test_data, desc='channels'):
    formatted = format_text(data)
    lang_code = predict_language(formatted)
    data.update({'lang_code': lang_code})
    if lang_code in TARGET_LANGS:
        target.append(data)
        
print('Number of channels with target language', len(target))

## Make predictions

# load models and train data
tgcat = load_models()
train_data = pd.read_csv(TRAIN_DATA)
train_data['description'].fillna('', inplace=True)
train_data['recent_posts'] = train_data['posts'].apply(eval)

# calculate scores
top_tasks = []
for l in tqdm(TARGET_LANGS, desc='langs'):
    subset = list(filter(lambda x: x['lang_code'] == l,
                         target))
    train_subset = train_data.query(f'language == "{l}"')
    raw,tokens = prepare_texts(subset, lang=l)
    embeddings = tgcat[l].vect(tokens)
    probs = tgcat[l].clf(embeddings)
    entropy = torch.sum(probs * torch.log(probs), dim=1)
    info_density = (-1) * torch.cdist(embeddings, embeddings, p=2).mean(1)
    train_embeddings = tgcat[l].vect(prepare_texts(train_subset.to_dict('records'), lang=l)[1])
    diversity = torch.cdist(embeddings, train_embeddings, p=2).mean(1)
    score = entropy * info_density * diversity
    top_score = score.argsort(0, descending=False)[:TOP_N]
    subset = pd.DataFrame(subset)
    subset['score'] = score
    subset['predictions'] = tgcat[l](tokens)
    subset['predictions'] = subset['predictions'].apply(json.dumps)
    one = subset.iloc[top_score.numpy()].to_dict('records')
    top_tasks.extend(one)

assert len(top_tasks) == TOP_N * len(TARGET_LANGS)
# Save tasks
for t in top_tasks:
    t['posts'] = '\n\n======================= NEXT POST =======================\n\n'.join(t['recent_posts'])
with open('data/processed/labelling_tasks_sample.json', 'w') as f:
    json.dump(top_tasks, f)
