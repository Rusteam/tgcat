"""
Create reference data from input data and output predictions
to be used in similarity search in the web app
"""
from pathlib import Path

from tqdm import tqdm

from src.train import REFERENCE_DATA, TGCAT_FILES, PROJECT_DIR
from src.train.text_utils import load_test_file, save_json
from src.train.download_etl import update_dict


KEEP_LANGS = list(TGCAT_FILES.keys())
OUTPUT_FOLDER = PROJECT_DIR / 'data/processed/reference'


def load_and_merge(in_file, out_file):
    """ load both inputs and outputs and merge them line by line deleting irrelvant languages """
    inputs = load_test_file(in_file, verbose=False)
    outputs = load_test_file(out_file, verbose=False)
    data = [update_dict(i,o) for i,o in zip(inputs, outputs) if o['lang_code'] in KEEP_LANGS]
    print(f"Keeping {len(data)} rows")
    return data


def run_all():
    """ load all files, merge and save them """
    for one in tqdm(REFERENCE_DATA, desc='loading files'):
        merged = load_and_merge(**one)
        stem = Path(one['in_file']).stem.split('-')[0]
        fpath = OUTPUT_FOLDER / f'{stem}.json'
        save_json(merged, fpath)


if __name__ == '__main__':
    run_all()
