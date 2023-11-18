"""Download a dataset from HuggingFace Datasets.
"""
from pathlib import Path

import fire
from datasets import load_dataset
from tqdm.auto import tqdm

lang_maps = dict(
    docker="dockerfile",
    apache_groovy="groovy",
    basic="realbasic",
    batch="batchfile",
    coffescript="coffeescript",
    common_lisp="common_lisp",
    cplusplus="c++",
    protobuf="protocol_buffer",
    objective_c="objective-c++",
    lisp="emacs_lisp",
    csharp="c-sharp",


)
exclude = [
    "other", "1s_enterprise", "actionscript",
    "apex", "delphi", "fift",
    "func", "hack", "tl"
]


def download_thestack(dest_dir="./data/raw/thestack",
                      n_samples=10, n_skip=0):
    lang_enums = Path(__file__).with_name("langs_enum_r2.txt").read_text().splitlines()
    dest_path = Path(__file__).parents[2] / dest_dir
    progress_bar = tqdm(lang_enums, desc="downloading languages")

    for lang in lang_enums[::-1]:
        req_lang = lang.split("_", maxsplit=2)[-1].lower()
        progress_bar.set_description(f"downloading {req_lang}")
        progress_bar.update(1)

        class_dir = dest_path / lang
        class_dir.mkdir(parents=True, exist_ok=True)

        if req_lang in exclude:
            continue
        elif req_lang in lang_maps:
            req_lang = lang_maps[req_lang]

        n_exist = len(list(class_dir.glob("*.txt")))
        if n_exist >= n_samples:
            continue

        try:
            ds = load_dataset(
                "bigcode/the-stack",
                data_dir=f"data/{req_lang}",
                split="train",
                streaming=True
            )

            if n_exist > 0 or n_skip > 0:
                ds = ds.skip(n_exist + n_skip)

            for idx, sample in enumerate(iter(ds.shuffle().take(n_samples - n_exist))):
                dest_file = class_dir / f"{idx+n_exist}.txt"
                dest_file.write_text(sample["content"])

        except Exception as e:
            print(f"Failed to download {req_lang}: {e}")


if __name__ == "__main__":
    fire.Fire(download_thestack)
