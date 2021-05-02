"""
helpers
"""
from tqdm.autonotebook import tqdm
import numpy as np
import pandas as pd



def flatten_category(labelled_data):
    """ convert multiple labels to multiple rows """
    data = []
    for i, row in tqdm(labelled_data.iterrows(), desc='rows'):
        for t,w in row['category'].items():
            row['topic'] = t
            row['weight'] = w
            data.append(row)
    data = pd.DataFrame(data)
    return data


rand_true = lambda test_prob: np.random.choice([True,False], p=[test_prob, 1 - test_prob])

def select_test(data, test_subsets=None,  test_size=0.3):
    """ Return True for test set and False for train """
    if test_subsets is None:
        test_subsets = data['subset'].unique().tolist()
    is_test = data.apply(lambda x: rand_true(test_size) if x['subset'] in test_subsets else False,
              axis=1)
    return is_test


def load_data(file):
    data = pd.read_csv(file,)
    data['description'].fillna("", inplace=True)
    data['category'] = data['category'].apply(eval)

    data.info()
    return data
