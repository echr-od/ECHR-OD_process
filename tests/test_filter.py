import pytest
from copy import deepcopy

from echr.steps.filter import split_and_format_article, format_cases, format_subarticle, format_article, format_parties,\
    format_conclusion, filter_cases, generate_statistics, merge_conclusion_elements, find_base_articles
from echr.utils.misc import compare_two_lists
from tests.data.test_filter_samples import merge_ccl, format_ccl, raw_cases_input, columns
from rich.console import Console


class TestFormatConclusion:

    @staticmethod
    @pytest.mark.parametrize("input,output", [('3', ['3']),
                                              ('5-1+6+7+p1-3', ['5-1', '6', '7', 'p1-3']),
                                              ('5-1+5-3', ['5-1', '5-3']),
                                              ('14+5-3', ['14', '5-3']),
                                              ('.2-a-c+,p3-1+#p41', ['2-a-c', 'p3-1', 'p41']),
                                              ('', [''])
                                              ])
    def test_split_and_format_article(input, output):
        res = split_and_format_article(article=input)
        assert sorted(res) == sorted(output)

    @staticmethod
    @pytest.mark.parametrize('input,output', [(['3'], ['3']),
                                              (['5', '6', '7', 'p1-3'], ['5', '6', '7', 'p1-3']),
                                              (['5-1', '5-3'], ['5', '5']),
                                              (['14+5-3'], ['14']),
                                              (['p4-4'], ['p4-4'])])
    def test_find_base_articles(input, output):
        res = find_base_articles(articles=input)
        assert sorted(res) == sorted(output)

    @staticmethod
    @pytest.mark.parametrize("input,output", merge_ccl)
    def test_merge_conclusion_elements(input, output):
        res = merge_conclusion_elements(input)
        print(res)
        assert compare_two_lists(res, output)

    @staticmethod
    @pytest.mark.parametrize("input,output", format_ccl)
    def test_format_conclusion(input, output):
        res = format_conclusion(input)
        assert (compare_two_lists(res, output))


class TestFormatParties:
    @staticmethod
    @pytest.mark.parametrize("input,output", [('CASE OF STAFEYEV v. RUSSIA', ['STAFEYEV', 'RUSSIA']),
                                              ('CASE OF SCHUMMER v. GERMANY(No. 1)', ['SCHUMMER', 'GERMANY']),
                                              ('CASE OF BARANIN AND VUKČEVIĆ v. MONTENEGRO',
                                               ['BARANIN AND VUKČEVIĆ', 'MONTENEGRO']),
                                              ('CASE OF TROCIN v. THE REPUBLIC OF MOLDOVA',
                                               ['TROCIN', 'THE REPUBLIC OF MOLDOVA']),
                                              ('CASE OF PAVEL SHISHKOV v. RUSSIA', ['PAVEL SHISHKOV', 'RUSSIA']),
                                              ('CASE OF G.V. v. ROMANIA', ['G.V.', 'ROMANIA']),
                                              ('CASE OF MOREIRA & FERREIRINHA , LDA AND OTHERS v. PORTUGAL',
                                               ['MOREIRA & FERREIRINHA , LDA AND OTHERS', 'PORTUGAL'])
                                              ])
    def test_format_parties(input, output):
        res = format_parties(input)
        assert (sorted(res) == sorted(output))


class TestFormatArticle:

    @staticmethod
    @pytest.mark.parametrize("input,output", [('5;5-1;7;7-1', ['5', '7']),
                                              ("1;7;7-1;14+7;14;30", ['1', '7', '14', '30']),
                                              ("1;14+7;14;P4-1", ['1', '7', '14', 'p4-1']),
                                              ("5-1;5-2;5-3;5-a-c", ["5"])
                                              ])
    def test_format_article(input, output):
        res = format_article(input)
        assert sorted(res) == sorted(output)

    @staticmethod
    @pytest.mark.parametrize("input, output", [('3', ['3']),
                                               ('1;7;7-1;14+7;14;30', ['1', '14', '30', '7', '7-1']),
                                               ('1;14+7;14;P4-1', ['1', '14', '7', 'P4-1'])
                                               ])
    def test_format_subarticle(input, output):
        res = format_subarticle(input)
        assert sorted(res) == sorted(output)


class TestFilterCases:
    @staticmethod
    def test_filtering_cases():
        res = filter_cases(deepcopy(raw_cases_input))
        assert len(res) == 2


prepare_cases = format_cases(Console(), deepcopy(raw_cases_input))


class TestFormatCases:
    @staticmethod
    @pytest.mark.parametrize("case", prepare_cases)
    def test_format_cases_columns(case):
        assert compare_two_lists(columns, list(case.keys()))

    @staticmethod
    @pytest.mark.parametrize("column", columns)
    def test_values_not_empty(column):
        assert prepare_cases[0][column]


class TestGenerateStatistics:
    @staticmethod
    def test_empty_dicts():
        case = [{}, {}, {}]
        expected = {'attributes': {}}
        res = generate_statistics(case)
        assert res == expected

    @staticmethod
    def test_all_same_inputs():
        case = [{'a': 'xyz'}, {'a': 'xyz'}, {'a': 'xyz'}, {'a': 'xyz'}]
        expected = {'attributes': {'a': {'cardinal': 1, 'density': 0.25}}}
        res = generate_statistics(case)
        assert res == expected

    @staticmethod
    def test_mixed_inputs():
        case = [{'a': 'xyz', 'b': [1, 2, 3]}, {'a': 'xy', 'b': [4, 5, 6]}, {'a': 'x', 'b': []}]
        expected = {'attributes': {'a': {'cardinal': 3, 'density': 1}, 'b': {'cardinal': 6, 'density': 2}}}
        res = generate_statistics(case)
        assert res == expected

    @staticmethod
    def test_conclusions_statistics():
        case = [{'conclusion': merge_ccl[0][1]}, {'conclusion': merge_ccl[1][1]}, {'conclusion': merge_ccl[2][1]}]
        expected = {'attributes': {'conclusion': {'cardinal': 4, 'density': 4 / 3}}}
        res = generate_statistics(case)
        assert res == expected
