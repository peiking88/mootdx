from unittest import mock

import pandas as pd
import pytest
from click.testing import CliRunner

from mootdx.__main__ import entry, _setup_verbose
from mootdx.logger import logger, setup_logging


class TestSetupVerbose:
    def test_verbose_true(self):
        original_handlers = len(logger.handlers)
        _setup_verbose(logger, verbose=True)
        assert len(logger.handlers) > original_handlers

    def test_verbose_false(self):
        original_handlers = len(logger.handlers)
        _setup_verbose(logger, verbose=0)
        assert len(logger.handlers) == original_handlers


class TestSetupLogging:
    def test_setup_logging_default(self):
        setup_logging()
        assert len(logger.handlers) == 1

    def test_setup_logging_level(self):
        import logging as lg
        setup_logging(level=lg.DEBUG)
        assert logger.level == lg.DEBUG


class TestEntry:
    def test_entry_no_command(self):
        runner = CliRunner()
        result = runner.invoke(entry, [])
        assert result.exit_code == 2  # click 无命令时返回 2

    def test_entry_help(self):
        runner = CliRunner()
        result = runner.invoke(entry, ['--help'])
        assert result.exit_code == 0
        assert '读取股票在线行情数据' in result.output

    def test_entry_version(self):
        runner = CliRunner()
        result = runner.invoke(entry, ['--version'])
        assert result.exit_code == 0


class TestQuotesCommand:
    def test_quotes_default(self):
        with mock.patch('mootdx.quotes.Quotes') as MockQuotes:
            mock_instance = mock.MagicMock()
            mock_instance.bars.return_value = pd.DataFrame({'close': [10.0]})
            MockQuotes.factory.return_value = mock_instance

            runner = CliRunner()
            result = runner.invoke(entry, ['quotes', '-s', '600000'])
            assert result.exit_code == 0

    def test_quotes_with_output(self, tmp_path):
        output = tmp_path / 'test.csv'
        with mock.patch('mootdx.quotes.Quotes') as MockQuotes:
            mock_instance = mock.MagicMock()
            mock_instance.bars.return_value = pd.DataFrame({'close': [10.0]})
            MockQuotes.factory.return_value = mock_instance

            runner = CliRunner()
            result = runner.invoke(entry, ['quotes', '-s', '600000', '-o', str(output)])
            assert result.exit_code == 0


class TestReaderCommand:
    def test_reader_default(self, tmp_path):
        tdxdir = tmp_path / 'fixtures'
        tdxdir.mkdir()

        with mock.patch('mootdx.reader.Reader') as MockReader:
            mock_instance = mock.MagicMock()
            mock_instance.daily.return_value = pd.DataFrame({'close': [10.0]})
            MockReader.factory.return_value = mock_instance

            runner = CliRunner()
            result = runner.invoke(entry, ['reader', '-d', str(tdxdir)])
            assert result.exit_code == 0


class TestServerCommand:
    def test_server_help(self):
        runner = CliRunner()
        result = runner.invoke(entry, ['bestip', '--help'])
        assert result.exit_code == 0


class TestAffairCommand:
    def test_affair_listfile(self):
        with mock.patch('mootdx.affair.Affair') as MockAffair:
            MockAffair.files.return_value = [{'filename': 'test.zip', 'filesize': 100, 'hash': 'abc'}]

            runner = CliRunner()
            result = runner.invoke(entry, ['affair', '-l'])
            assert result.exit_code == 0
            assert 'test.zip' in result.output

    def test_affair_fetch_all(self, tmp_path):
        downdir = tmp_path / 'dl'
        with mock.patch('mootdx.affair.Affair') as MockAffair:
            MockAffair.files.return_value = [{'filename': 'test.zip', 'filesize': 100, 'hash': 'abc'}]
            MockAffair.fetch.return_value = True

            runner = CliRunner()
            result = runner.invoke(entry, ['affair', '-a', '-d', str(downdir)])
            assert result.exit_code == 0

    def test_affair_fetch_file(self, tmp_path):
        downdir = tmp_path / 'dl'
        with mock.patch('mootdx.affair.Affair') as MockAffair:
            MockAffair.files.return_value = [{'filename': 'test.zip', 'filesize': 100, 'hash': 'abc'}]
            MockAffair.fetch.return_value = True

            runner = CliRunner()
            result = runner.invoke(entry, ['affair', '-f', 'test.zip', '-d', str(downdir)])
            assert result.exit_code == 0

    def test_affair_parse_file(self, tmp_path):
        downdir = tmp_path / 'dl'
        downdir.mkdir()
        with mock.patch('mootdx.affair.Affair') as MockAffair:
            MockAffair.files.return_value = [{'filename': 'test.zip', 'filesize': 100, 'hash': 'abc'}]
            MockAffair.parse.return_value = 'parsed data'

            runner = CliRunner()
            result = runner.invoke(entry, ['affair', '-p', 'test.zip', '-d', str(downdir)])
            assert result.exit_code == 0

    def test_affair_parse_not_found(self):
        with mock.patch('mootdx.affair.Affair') as MockAffair:
            MockAffair.files.return_value = [{'filename': 'other.zip', 'filesize': 100, 'hash': 'abc'}]

            runner = CliRunner()
            result = runner.invoke(entry, ['affair', '-p', 'test.zip'])
            assert result.exit_code == 0


class TestBundleCommand:
    def test_bundle_default(self, tmp_path):
        output = tmp_path / 'bundle'
        with mock.patch('mootdx.quotes.Quotes') as MockQuotes:
            mock_instance = mock.MagicMock()
            mock_instance.bars.return_value = pd.DataFrame({'close': [10.0]})
            MockQuotes.factory.return_value = mock_instance

            runner = CliRunner()
            result = runner.invoke(entry, ['bundle', '-s', '600000', '-o', str(output)])
            assert result.exit_code == 0
