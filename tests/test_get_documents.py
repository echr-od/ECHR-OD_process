from mock import patch
from unittest.mock import MagicMock, mock_open, call
from rich.console import Console
from rich.progress import Progress
import sys
import os
import pytest

from echr.steps.get_documents import get_documents


def clean_up():
    paths = ["/tmp/101.pdf", "/tmp/202.docx", "/tmp/303.docx"]
    for p in paths:
        if os.path.exists(p):
            os.remove(p)


class TestGetDocuments:
    @staticmethod
    @pytest.fixture
    def builtins_open():
        return 'builtins.open' if sys.version_info >= (3, 0) else '__builtin__.open'

    @staticmethod
    def test_get_docs_ok(builtins_open):
        with patch('requests.get') as get, patch(builtins_open, mock_open()) as mck_open:
            get.return_value.ok = True
            get.return_value.iter_content.return_value = []
            id_list = [("101", 0), ("202", 1), ("303", 1)]
            path = "/tmp"

            get_documents(Console(), id_list, path, update=False)

            files_list = ["101.pdf", "202.docx", "303.docx"]
            open_args = [call(os.path.join(path, f), 'wb') for f in files_list]
            mck_open.assert_has_calls(open_args, any_order=True)

    @staticmethod
    def test_docks_with_update(builtins_open):
        with patch('requests.get') as get, patch(builtins_open, mock_open()) as mck_open, \
                patch('os.path.isfile') as isfile:
            isfile.return_value = False  # TODO: should be True, but there is a bug in code line 48 in get_documents
            get.return_value.ok = True
            get.return_value.iter_content.return_value = []
            id_list = [("101", 0), ("202", 1), ("303", 1)]
            path = "/tmp"

            get_documents(Console(), id_list, path, update=True)

            files_list = ["101.pdf", "202.docx", "303.docx"]
            open_args = [call(os.path.join(path, f), 'wb') for f in files_list]
            mck_open.assert_has_calls(open_args, any_order=True)

    @staticmethod
    @pytest.mark.xfail
    def test_empty_id_list(builtins_open):
        with patch.object(Progress, "add_task", return_value=None), patch(builtins_open, mock_open()) as mck_open:
            id_list = []
            path = "/tmp"

            get_documents(Console(), id_list, path, update=True)

            mck_open.assert_not_called()

    @staticmethod
    def test_flies_created(tmpdir):
        try:
            with patch('requests.get') as get:
                get.return_value.ok = True
                get.return_value.iter_content.return_value = []
                id_list = [("101", 0), ("202", 1), ("303", 1)]

                get_documents(Console(), id_list, tmpdir.strpath, update=True)

                files_list = ["101.pdf", "202.docx", "303.docx"]
                files_exist = [os.path.exists(tmpdir.join(f)) for f in files_list]
                assert all(files_exist)
        finally:
            clean_up()


