import json

from echr.steps.filter import format_conclusion, find_base_articles, split_and_format_article
from echr.utils.misc import compare_two_lists

class TestFormatConclusion:

    def test_split_and_format_article(self):
        article_examples = [
            {'input': '3', 'output': ['3']},
            {'input': '5-1+6+7+p1-3', 'output': ['5-1', '6', '7', 'p1-3']},
            {'input': '5-1+5-3', 'output': ['5-1', '5-3']},
            {'input': '14+5-3', 'output': ['14', '5-3']},
        ]

        for e in article_examples:
            res = split_and_format_article(article=e['input'])
            print(res, e['output'])
            assert (sorted(res) == sorted(e['output']))

    def test_find_base_articles(self):
        base_article_examples = [
            {'input': ['3'], 'output': ['3']},
            {'input': ['5', '6', '7', 'p1-3'], 'output': ['5', '6', '7', 'p1-3']},
            {'input': ['5-1', '5-3'], 'output': ['5', '5']},
            {'input': ['14+5-3'], 'output': ['14']},
            {'input': ['p4-4'], 'output': ['p4-4']}
        ]

        for e in base_article_examples:
            res = find_base_articles(articles=e['input'])
            print(res, e['output'])
            assert (sorted(res) == sorted(e['output']))

    def test_format_conclusion(self):
        with open('tests/data/sample_format_conclusion.json') as json_file:
            conclusions_examples = json.load(json_file)

        for e in conclusions_examples:
            res = format_conclusion(e['input'])
            assert (compare_two_lists(res, e['output']))

