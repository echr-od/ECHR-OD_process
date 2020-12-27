import json

from echr.steps.filter import format_conclusion, find_base_articles, split_and_format_article, format_parties, \
    merge_conclusion_elements, format_article, format_subarticle
from echr.utils.misc import compare_two_lists

class TestFormatConclusion:

    @staticmethod
    def test_split_and_format_article():
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

    @staticmethod
    def test_find_base_articles():
        base_article_examples = [
            {'input': ['3'], 'output': ['3']},
            {'input': ['5', '6', '7', 'p1-3'], 'output': ['5', '6', '7', 'p1-3']},
            {'input': ['5-1', '5-3'], 'output': ['5', '5']},
            {'input': ['14+5-3'], 'output': ['14']},
            {'input': ['p4-4'], 'output': ['p4-4']}
        ]

        for e in base_article_examples:
            res = find_base_articles(articles=e['input'])
            assert (sorted(res) == sorted(e['output']))

    @staticmethod
    def test_merge_conclusion_elements():
        merge_conclusion_elements_examples = [
            {'input': [
                {
                        "article": "2",
                        "base_article": "2",
                        "details": ["substantive aspect"],
                        "element": "Violation of Art. 2",
                        "type": "violation"
                },
                {
                        "article": "2",
                        "base_article": "2",
                        "element": "Violation of Art. 2",
                        "type": "violation"
                },
            ],
            'output': [
                {
                        "article": "2",
                        "base_article": "2",
                        "details": [
                            "substantive aspect"
                        ],
                        "element": "Violation of Art. 2",
                        "type": "violation"
                },
            ]
            }
        ]

        for e in merge_conclusion_elements_examples:
            res = merge_conclusion_elements(e['input'])
            assert (sorted(res) == sorted(e['output']))

    @staticmethod
    def test_format_conclusion():
        with open('tests/data/sample_format_conclusion.json') as json_file:
            conclusions_examples = json.load(json_file)

        for e in conclusions_examples:
            res = format_conclusion(e['input'])
            assert (compare_two_lists(res, e['output']))


class TestFormatParties:

    @staticmethod
    def test_format_parties():
        parties_examples = [
            {'input': 'CASE OF STAFEYEV v. RUSSIA', 'output': ['STAFEYEV', 'RUSSIA']},
            {'input': 'CASE OF SCHUMMER v. GERMANY(No. 1)', 'output': ['SCHUMMER', 'GERMANY']}
        ]

        for e in parties_examples:
            res = format_parties(e['input'])
            assert (sorted(res) == sorted(e['output']))


class TestFormatArticle:

    @staticmethod
    def test_format_article():
        format_article_examples = [
            {'input': '5;5-1;7;7-1', 'output': ['5', '7']},
            {'input': "1;7;7-1;14+7;14;30", 'output': ['1', '7', '14', '30']},
            {'input': "1;14+7;14;P4-1", 'output': ['1', '7', '14', 'p4-1']}
        ]
        for e in format_article_examples:
            res = format_article(e['input'])
            assert (sorted(res) == sorted(e['output']))

    @staticmethod
    def test_format_subarticle():
        format_subarticle_examples = [
            {'input': '3', 'output': ['3']},
            {'input': '1;7;7-1;14+7;14;30', 'output': ['1', '14', '30', '7', '7-1']},
            {'input': '1;14+7;14;P4-1', 'output': ['1', '14', '7', 'P4-1']},
        ]
        for e in format_subarticle_examples:
            res = format_subarticle(e['input'])
            assert (sorted(res) == sorted(e['output']))