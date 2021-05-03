"""
compare c++ outputs to python
"""
from pathlib import Path
import unittest
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd
# custom
from src.train.predict import load_test_file

OUTPUTS = [
    {
        "c++": "data/processed/dc0415-category_output.txt",
        "py": "data/processed/dc0415-input-all.txt"
    },
]


def read_file(filepath):
    lines = Path(filepath).read_text().strip().split('\n')
    lines = list(map(eval, lines))
    return lines


class OutputTester(unittest.TestCase):
    def setUp(self):
        self.data = [{
            'c++': read_file(files['c++']),
            'py': read_file(files['py'])
        } for files in OUTPUTS]


    def test_lang_codes(self,):
        """ compare language predictions """
        for data in self.data:
            langs = pd.DataFrame(dict(
                src = list(map(lambda x: x['lang_code'], data['py'])),
                dest = list(map(lambda x: x['lang_code'], data['c++'])),
            ))
            langs['is_equal'] = langs['src'] == langs['dest']
            print("LANGUAGE TESTS:")
            print(classification_report(langs['src'], langs['dest']))
            print(pd.crosstab(langs['src'], langs['dest']))
            acc = accuracy_score(langs['src'], langs['dest'])
            # langs.to_csv('tests/language_test_output.csv', index=True)
            self.assertTrue(acc > 0.99)


    def test_topics(self):
        """ compare topic predictions """
        for data in self.data:
            topics = pd.DataFrame(dict(
                src=list(map(lambda x: x['category'], data['py'])),
                dest=list(map(lambda x: x['category'], data['c++'])),
            ))
            topics['len_equal'] = topics['src'].apply(len) == topics['dest'].apply(len)
            topics['match_score'] = topics.apply(lambda x: self.compare_topics(x['src'], x['dest']),
                                                 axis=1)
            topics['is_correct'] = topics['match_score'] == 1.0
            # topics.to_csv('tests/category_test_output.csv', index=False)
            print("TOPIC TESTS:")
            self.assertTrue(topics['match_score'].mean() > 0.99, msg="\n".join([
                f"length score: {topics['len_equal'].mean()}",
                f"Topic match score: {topics['match_score'].mean()}"
                ]))


    @staticmethod
    def compare_topics(src, dest):
        src_topics = set(src.keys())
        dest_topics = set(dest.keys())
        if len(src_topics) == 0 and len(dest_topics) == 0:
            return 1.0
        elif len(src_topics) == 0 or len(dest_topics) == 0:
            return 0.0
        else:
            src_match = len(src_topics.intersection(dest_topics)) / len(src_topics)
            dest_match = len(dest_topics.intersection(src_topics)) / len(dest_topics)
            return (src_match + dest_match) / 2


if __name__ == '__main__':
    unittest.main()