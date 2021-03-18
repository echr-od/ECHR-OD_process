import json
import re
from docx import Document

from echr.steps.preprocess_documents import para_to_text

class TestPreprocessWord:

    @staticmethod
    def test_para_to_text():
        file = 'tests/data/judgments/001-83979.docx'
        expected_file = 'tests/data/judgments/001-83979_without_smarttags.docx'
        doc = Document(file)
        expected_doc = Document(expected_file)
        broken_list_paragraphs = []
        fixed_list_paragraphs = []
        expected_list_paragraphs = []

        for p in doc.paragraphs:
            broken_list_paragraphs.append(p.text)
            fixed_list_paragraphs.append(para_to_text(p))

        for p in expected_doc.paragraphs:
            expected_list_paragraphs.append(para_to_text(p))

        broken_list_paragraphs = [p for p in broken_list_paragraphs if p]
        fixed_list_paragraphs = [p for p in fixed_list_paragraphs if p]
        expected_list_paragraphs = [p for p in expected_list_paragraphs if p]
        assert len(fixed_list_paragraphs) == len(expected_list_paragraphs)
        for i, p in enumerate(fixed_list_paragraphs):
            assert p == expected_list_paragraphs[i]

        broken_different_from_expected = any(
            [p != expected_list_paragraphs[i] for i, p in enumerate(broken_list_paragraphs)])
        broken_different_from_fixed = any([p != fixed_list_paragraphs[i] for i, p in enumerate(broken_list_paragraphs)])
        fixed_equals_expected = all([p == fixed_list_paragraphs[i] for i, p in enumerate(expected_list_paragraphs)])

        assert broken_different_from_expected
        assert broken_different_from_fixed
        assert fixed_equals_expected
