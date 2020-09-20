from mock import patch
from unittest.mock import MagicMock
import json
import os

from echr.steps.cases_info import determine_max_documents, get_case_info

class TestDetermineMaxDocuments:

    @patch('requests.get')
    def test_ok(self, get):
        get.return_value = MagicMock(ok=True,
                                     content=json.dumps({"resultcount": 169351,"results":[]}))

        rc, n = determine_max_documents(base_url="", default_value=-1)
        assert rc == 0
        assert n == 169351

    @patch('requests.get')
    def test_nok(self, get):
        get.return_value = MagicMock(ok=False,
                                     content=json.dumps({"resultcount": 169351,"results":[]}))

        rc, n = determine_max_documents(base_url="", default_value=100)
        assert rc == 1
        assert n == 100

    @patch('requests.get')
    def test_ok_no_count(self, get):
        get.return_value = MagicMock(ok=True,
                                     content=json.dumps({"results":[]}))

        rc, n = determine_max_documents(base_url="", default_value=100)
        assert rc == 1
        assert n == 100

    @patch('requests.get')
    def test_ok_count_not_int(self, get):
        get.return_value = MagicMock(ok=True,
                                     content=json.dumps({"resultcount": "should_not_happen", "results": []}))

        rc, n = determine_max_documents(base_url="", default_value=100)
        assert rc == 1
        assert n == 100


class TestGetCasesInfo:

    def test_negative_document_number(self):
        rc = get_case_info(base_url="", max_documents=-1, path='/tmp')
        assert rc == 2

    @patch('requests.get')
    def test_ok(self, get):
        content = json.dumps({"content": "test"})
        get.return_value = MagicMock(ok=True,
                                     content=content)

        rc = get_case_info(base_url="", max_documents=100, path='/tmp/')
        assert rc == 0
        assert os.path.isfile('/tmp/0.json')

    @patch('requests.get')
    def test_ok_large_number(self, get):
        content = json.dumps({"content": "test"})
        get.return_value = MagicMock(ok=True,
                                     content=json.dumps(content))

        rc = get_case_info(base_url="", max_documents=950, path='/tmp/')
        assert rc == 0
        assert os.path.isfile('/tmp/0.json')
        assert os.path.isfile('/tmp/500.json')
        assert not os.path.isfile('/tmp/1000.json')

    @patch('requests.get')
    def test_nok(self, get):
        get.return_value = MagicMock(ok=False,
                                     content=json.dumps({"resultcount": "120", "results": []}))

        rc = get_case_info(base_url="", max_documents=100, path='/tmp/')
        assert rc == 1
        assert os.stat('/tmp/0.json').st_size == 0
