import pytest

from mootdx.exceptions import (
    FileNeedRefresh,
    MootdxException,
    MootdxModuleNotFoundError,
    MootdxValidationException,
)


class TestMootdxException:
    def test_basic(self):
        e = MootdxException(message='test message')
        assert str(e) == 'test message'

    def test_with_provider(self):
        e = MootdxException(provider='test_provider', message='error')
        assert e.provider == 'test_provider'
        assert e.message == 'error'

    def test_with_response(self):
        e = MootdxException(response={'code': 500}, message='error')
        assert e.response == {'code': 500}

    def test_with_data(self):
        e = MootdxException(data={'key': 'value'}, message='error')
        assert e.data == {'key': 'value'}

    def test_no_message(self):
        e = MootdxException()
        assert e.message is None

    def test_repr(self):
        e = MootdxException(message='connection failed')
        assert repr(e) == '<MOOTDXError: connection failed>'

    def test_is_exception(self):
        with pytest.raises(MootdxException):
            raise MootdxException('test')


class TestMootdxValidationException:
    def test_basic(self):
        e = MootdxValidationException('invalid')
        assert isinstance(e, Exception)

    def test_args_ignored(self):
        e = MootdxValidationException('anything', foo='bar')
        assert isinstance(e, Exception)


class TestMootdxModuleNotFoundError:
    def test_basic(self):
        e = MootdxModuleNotFoundError('module not found')
        assert isinstance(e, Exception)


class TestFileNeedRefresh:
    def test_is_file_not_found(self):
        e = FileNeedRefresh()
        assert isinstance(e, FileNotFoundError)
