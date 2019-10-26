#!/usr/bin/python3
import sys

import mock
import pytest

# import shutil


@pytest.fixture
def mock_layers():
    sys.modules["charms.layer"] = mock.Mock()
    sys.modules["reactive"] = mock.Mock()


@pytest.fixture
def mock_action_get(monkeypatch):

    def mock_action_get(name):
        return 'blah'

    monkeypatch.setattr('charmhelpers.core.hookenv.action_get',
                        mock_action_get)
    return mock_action_get


@pytest.fixture
def mock_action_set(monkeypatch):

    mock_action_set = mock.Mock()
    monkeypatch.setattr('charmhelpers.core.hookenv.action_set',
                        mock_action_set)
    return mock_action_set


@pytest.fixture
def mock_action_fail(monkeypatch):

    mock_action_fail = mock.Mock()
    monkeypatch.setattr('charmhelpers.core.hookenv.action_fail',
                        mock_action_fail)
    return mock_action_fail


@pytest.fixture
def mock_juju_unit(monkeypatch):

    def mock_local_unit():
        return 'mocked'

    monkeypatch.setattr('charmhelpers.core.hookenv.local_unit',
                        mock_local_unit)
    return mock_local_unit


@pytest.fixture
def mock_check_call(monkeypatch):
    mock_call = mock.Mock()
    monkeypatch.setattr('libsmb.check_call', mock_call)
    return mock_call


@pytest.fixture
def mock_check_output(monkeypatch):

    def mock_output(args, *, kwargs={}):
        if args == ['samba-tool', 'user', 'list']:
            return "ubuntu"
        else:
            return True

    monkeypatch.setattr('libsmb.check_output', mock_output)
    return mock_output


@pytest.fixture
def mock_service(monkeypatch):

    mock_service = mock.Mock(return_value=True)
    monkeypatch.setattr('libsmb.service', mock_service)
    return mock_service


@pytest.fixture
def mock_hookenv_config(monkeypatch):
    import yaml

    def mock_config():
        cfg = {}
        yml = yaml.load(open('./config.yaml'))

        # Load all defaults
        for key, value in yml['options'].items():
            cfg[key] = value['default']

        return cfg

    monkeypatch.setattr('libsmb.hookenv.config', mock_config)


@pytest.fixture
def smb(tmpdir, mock_layers, mock_hookenv_config, mock_check_call,
        mock_check_output, mock_service, monkeypatch):
    from libsmb import SambaHelper
    smb = SambaHelper()

    # Set correct charm_dir
    monkeypatch.setattr('libsmb.hookenv.charm_dir', lambda: '.')

    # Patch the combined exports file to a tmpfile
    config_file = tmpdir.join("smb.conf")
    smb.config_file = config_file.strpath
    smb.reload_config()

    # Any other functions that load PH will get this version
    monkeypatch.setattr('libsmb.SambaHelper', lambda: smb)

    return smb
