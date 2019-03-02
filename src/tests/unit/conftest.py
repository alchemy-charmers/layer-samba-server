#!/usr/bin/python3
import pytest
import mock

import sys
# import shutil


@pytest.fixture
def mock_layers():
    sys.modules["charms.layer"] = mock.Mock()
    sys.modules["reactive"] = mock.Mock()


@pytest.fixture
def mock_check_call(monkeypatch):
    mock_call = mock.Mock()
    monkeypatch.setattr('libsmb.subprocess.check_call', mock_call)
    return mock_call


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
def smb(tmpdir, mock_layers, mock_hookenv_config, monkeypatch):
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
