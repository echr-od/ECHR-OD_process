from mock import patch
from unittest.mock import MagicMock
import json
import os
from rich.console import Console

from echr.steps.cases_info import determine_max_documents, get_case_info


class TestGetCasesInfo:

    @staticmethod
    def test_negative_document_number():
        rc = get_case_info(Console(), base_url="", max_documents=-1, path='/tmp')
        assert rc == 2

    '''
    @staticmethod
    @patch('requests.get')
    def test_ok(get):
        content = json.dumps({"content": "test"})
        get.return_value = MagicMock(ok=True,
                                     content=content)

        rc = get_case_info(Console(), base_url="", max_documents=100, path='/tmp/')
        assert rc == 0
        assert os.path.isfile('/tmp/0.json')

    @staticmethod
    @patch('requests.get')
    def test_ok_large_number(get):
        content = json.dumps({"content": "test"})
        get.return_value = MagicMock(ok=True,
                                     content=json.dumps(content))

        rc = get_case_info(Console(), base_url="", max_documents=950, path='/tmp/')
        assert rc == 0
        assert os.path.isfile('/tmp/0.json')
        assert os.path.isfile('/tmp/500.json')
        assert not os.path.isfile('/tmp/1000.json')

    @staticmethod
    @patch('requests.get')
    def test_nok(get):
        get.return_value = MagicMock(ok=False,
                                     content=json.dumps({"resultcount": "120", "results": []}))

        rc = get_case_info(Console(), base_url="", max_documents=100, path='/tmp/')
        assert rc == 1
        assert not os.path.isfile('/tmp/0.json')
    '''