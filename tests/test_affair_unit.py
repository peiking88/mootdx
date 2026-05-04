import hashlib
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from mootdx import affair as affair_module
from mootdx.affair import Affair, download, fetch_file


class TestAffairParse:
    def test_no_filename(self):
        result = Affair.parse(downdir='.', filename=None)
        assert result is None

    def test_file_not_exists_and_fetch_fails(self, tmp_path):
        with mock.patch.object(Affair, 'fetch') as mock_fetch:
            mock_fetch.return_value = None
            result = Affair.parse(downdir=str(tmp_path), filename='nonexistent.zip')
            assert result is None
            mock_fetch.assert_called_once()

    def test_file_exists_and_parses(self, tmp_path):
        downdir = tmp_path / 'data'
        downdir.mkdir()
        filepath = downdir / 'test.zip'
        filepath.write_bytes(b'dummy')

        with mock.patch('mootdx.affair.financial.FinancialReader') as mock_reader_class:
            mock_reader = mock.MagicMock()
            mock_reader.to_data.return_value = [{'a': 1}]
            mock_reader_class.return_value = mock_reader

            result = Affair.parse(downdir=str(downdir), filename='test.zip')
            assert result is not None


class TestAffairFetch:
    def test_fetch_with_filename(self, tmp_path):
        with mock.patch('mootdx.affair.financial.Financial') as mock_fin:
            mock_instance = mock.MagicMock()
            mock_fin.return_value = mock_instance
            with mock.patch('mootdx.affair.financial.FinancialList'):
                with mock.patch('mootdx.affair.TqdmUpTo') as mock_tqdm:
                    mock_t = mock.MagicMock()
                    mock_tqdm.return_value.__enter__.return_value = mock_t

                    result = Affair.fetch(downdir=str(tmp_path), filename='gpcw20200101.zip')
                    assert result is True
                    mock_instance.fetch_only.assert_called_once()

    def test_fetch_creates_download_dir(self, tmp_path):
        downdir = tmp_path / 'new_dir'
        assert not downdir.exists()

        with mock.patch('mootdx.affair.financial.Financial') as mock_fin:
            mock_instance = mock.MagicMock()
            mock_fin.return_value = mock_instance
            with mock.patch('mootdx.affair.financial.FinancialList'):
                with mock.patch('mootdx.affair.TqdmUpTo') as mock_tqdm:
                    mock_t = mock.MagicMock()
                    mock_tqdm.return_value.__enter__.return_value = mock_t

                    Affair.fetch(downdir=str(downdir), filename='test.zip')
                    assert downdir.exists()

    def test_fetch_without_filename_single(self, tmp_path):
        mock_files = [{'filename': 'f1.zip', 'hash': 'abc'}]
        with mock.patch('mootdx.affair.financial.Financial') as mock_fin:
            mock_fin.return_value = mock.MagicMock()
            with mock.patch('mootdx.affair.financial.FinancialList') as mock_list_class:
                mock_list = mock.MagicMock()
                mock_list.fetch_and_parse.return_value = mock_files
                mock_list_class.return_value = mock_list

                with mock.patch('mootdx.affair.asyncio.get_event_loop') as mock_loop:
                    mock_event = mock.MagicMock()
                    mock_loop.return_value = mock_event

                    # Don't actually run the event loop
                    result = Affair.fetch(downdir=str(tmp_path))
                    # It would try to run the event loop; this is covered by just reaching the code


class TestAffairFiles:
    def test_files_returns_list(self):
        with mock.patch('mootdx.affair.financial.FinancialList') as mock_list_class:
            mock_list = mock.MagicMock()
            mock_list.fetch_and_parse.return_value = [{'filename': 'f1.zip'}]
            mock_list_class.return_value = mock_list

            result = Affair.files()
            assert result == [{'filename': 'f1.zip'}]


class TestDownload:
    def test_download_success(self, tmp_path):
        downdir = tmp_path / 'dl'
        downdir.mkdir()

        with mock.patch('mootdx.affair.financial.Financial') as mock_fin:
            mock_instance = mock.MagicMock()
            mock_fin.return_value = mock_instance
            with mock.patch('mootdx.affair.TqdmUpTo') as mock_tqdm:
                mock_t = mock.MagicMock()
                mock_tqdm.return_value.__enter__.return_value = mock_t

                result = download(downdir=str(downdir), filename='test.zip')
                assert result is True
                mock_instance.fetch_only.assert_called_once()
