import plugins.module_utils.mailman as mailman
import pytest

from io import BytesIO
from unittest import mock


@pytest.fixture
def mm():
    mm = mailman.Mailman()
    return mm


@pytest.fixture()
def mock_subprocess(monkeypatch):
    _mock_subprocess = mock.Mock()
    monkeypatch.setattr(mailman, 'subprocess', _mock_subprocess)

    return _mock_subprocess


class FakeFile(BytesIO):
    def __init__(self, name):
        self.name = name
        super().__init__()

    def close(self):
        return


def test_invalid_commands(mm):
    with pytest.raises(mailman.InvalidCommandError):
        mm.run('/fake')
    with pytest.raises(mailman.InvalidCommandError):
        mm.run('../fake')


def test_failing_command(mock_subprocess, mm):
    mock_popen = mock.Mock()
    mock_subprocess.Popen.return_value = mock_popen
    mock_popen.communicate.return_value = (b'out', b'err')
    mock_popen.wait.return_value = 13

    with pytest.raises(mailman.CalledProcessError) as err:
        mm.run('fake')

    assert err.value.returncode == 13
    assert err.value.stdout == b'out'
    assert err.value.stderr == b'err'
    assert err.value.command == 'fake'


def test_normal_command(mock_subprocess, mm):
    mock_popen = mock.Mock()
    mock_subprocess.Popen.return_value = mock_popen
    mock_popen.communicate.return_value = (b'out', b'err')
    mock_popen.wait.return_value = 0

    res = mm.run('fake')
    assert res == 'out'


def test_raw_command(mock_subprocess, mm):
    mock_popen = mock.Mock()
    mock_subprocess.Popen.return_value = mock_popen
    mock_popen.communicate.return_value = (b'out', b'err')
    mock_popen.wait.return_value = 0

    res = mm.run('fake', raw=True)
    assert res == b'out'


def test_list_lists(mock_subprocess, mm):
    mock_popen = mock.Mock()
    mock_subprocess.Popen.return_value = mock_popen
    mock_popen.communicate.return_value = (b'list1\nlist2\n', b'')
    mock_popen.wait.return_value = 0

    res = mm.list_lists()
    assert mock_subprocess.Popen.call_args[0] == (
        ['/usr/lib/mailman/bin/list_lists', '-b'],)
    assert res == ['list1', 'list2']


def test_list_members(mock_subprocess, mm):
    mock_popen = mock.Mock()
    mock_subprocess.Popen.return_value = mock_popen
    mock_popen.communicate.return_value = (b'member1\nmember2\n', b'')
    mock_popen.wait.return_value = 0

    res = mm.list_regular_members('example')
    assert mock_subprocess.Popen.call_args[0] == (
        ['/usr/lib/mailman/bin/list_members', '-r', 'example'],)
    assert res == ['member1', 'member2']


def test_get_list_config(mock_subprocess, mm):
    sample_config = '''
    # Here is an example config item
    testitem = 'testvalue'
    '''
    sample_config = '\n'.join(line.lstrip() for line in sample_config.splitlines())
    mock_popen = mock.Mock()
    mock_subprocess.Popen.return_value = mock_popen
    mock_popen.communicate.return_value = (sample_config, '')
    mock_popen.wait.return_value = 0

    res = mm.get_list_config('example')
    assert mock_subprocess.Popen.call_args[0] == (
        ['/usr/lib/mailman/bin/config_list', '-o', '-', 'example'],)
    assert res['testitem'] == 'testvalue'


def test_set_list_config(monkeypatch, mock_subprocess, mm):
    sample_config = {
        'testitem': 'testvalue',
    }
    expected_output = b'true = True\nfalse = False\ntestitem = "testvalue"\n'

    mock_popen = mock.Mock()
    mock_subprocess.Popen.return_value = mock_popen
    mock_popen.communicate.return_value = (b'out', b'err')
    mock_popen.wait.return_value = 0

    buf = FakeFile('fakefile')

    mock_tempfile = mock.Mock()
    monkeypatch.setattr(mailman, 'tempfile', mock_tempfile)
    mock_tempfile.NamedTemporaryFile.return_value = buf

    mm.set_list_config('example', sample_config)
    assert mock_subprocess.Popen.call_args[0] == (
        ['/usr/lib/mailman/bin/config_list', '-i', buf.name, 'example'],)
    assert buf.getvalue() == expected_output
