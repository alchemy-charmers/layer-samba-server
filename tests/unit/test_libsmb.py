#!/usr/bin/python3
import shutil


class TestLibsmb():

    def test_pytest(self):
        assert True

    def test_smb(self, smb):
        ''' See if the smb fixture works to load charm configs '''
        assert isinstance(smb.charm_config, dict)

    def test_clean_example_config(self, smb):
        shutil.copyfile("./tests/unit/smb.conf", smb.config_file)
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "# Sample configuration file" in cfg
            assert ";[profiles]" in cfg
            assert "[printers]" in cfg
            assert "[print$]" in cfg
        smb.clean_example_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "# Sample configuration file" not in cfg
            assert ";[profiles]" not in cfg
            assert "[printers]" in cfg
            assert "[print$]" in cfg

    def test_update_config(self, smb, mock_check_call):
        shutil.copyfile("./tests/unit/smb.clean", smb.config_file)
        smb.reload_config()
        # Check default settings write w/o error
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[printers]" not in cfg
            assert "[print$]" not in cfg
            assert "[global]" in cfg

        # Check with one share
        smb.charm_config['smb-shares'] = '/mnt/unit-test'
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[/mnt/unit-test]" in cfg
            assert "browsable = yes\n" in cfg
            assert "guest = ok\n" in cfg
            assert "read only = no\n" in cfg
            assert "create mask = 0777\n" in cfg

        # Check with multiple share
        smb.charm_config['smb-shares'] = '/mnt/unit-test,/mnt/test-unit'
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[/mnt/unit-test]" in cfg
            assert "[/mnt/test-unit]" in cfg
            assert "browsable = yes\n" in cfg
            assert "guest = ok\n" in cfg
            assert "read only = no\n" in cfg
            assert "create mask = 0777\n" in cfg

        # Check browsable
        smb.charm_config['smb-shares'] = '/mnt/unit-test,/mnt/test-unit'
        smb.charm_config['smb-browsable'] = False
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[/mnt/unit-test]" in cfg
            assert "[/mnt/test-unit]" in cfg
            assert "browsable = yes\n" not in cfg
            assert "browsable = no\n" in cfg
            assert "guest = ok\n" in cfg
            assert "read only = no\n" in cfg
            assert "create mask = 0777\n" in cfg

        # Check guest
        smb.charm_config['smb-shares'] = '/mnt/unit-test,/mnt/test-unit'
        smb.charm_config['smb-guest'] = False
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[/mnt/unit-test]" in cfg
            assert "[/mnt/test-unit]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest = ok\n" not in cfg
            assert "guest = no\n" in cfg
            assert "read only = no\n" in cfg
            assert "create mask = 0777\n" in cfg

        # Check read only
        smb.charm_config['smb-shares'] = '/mnt/unit-test,/mnt/test-unit'
        smb.charm_config['smb-read-only'] = True
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[/mnt/unit-test]" in cfg
            assert "[/mnt/test-unit]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest = no\n" in cfg
            assert "read only = no\n" not in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0777\n" in cfg

        # Check removal of section
        smb.charm_config['smb-shares'] = '/mnt/unit-test'
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[/mnt/unit-test]" in cfg
            assert "[/mnt/test-unit]" not in cfg
            assert "browsable = no\n" in cfg
            assert "guest = no\n" in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0777\n" in cfg

        # Check custom config
        smb.charm_config['smb-custom'] = 'path=/mnt/custom,shadow:format=zfsnap_%S_%Y-%m-%d_%H.%M.00--10y,vfs objects=shadow_copy'
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[custom-0]" in cfg
            assert "path = /mnt/custom\n" in cfg
            assert "shadow:format = zfsnap_%S_%Y-%m-%d_%H.%M.00--10y\n" in cfg
            assert "vfs objects = shadow_copy\n" in cfg

        # Check multiple custom configs
        smb.charm_config['smb-custom'] = ('path=/mnt/custom,'
                                          'shadow:format=zfsnap_%S_%Y-%m-%d_%H.%M.00--10y,'
                                          'vfs objects=shadow_copy;'
                                          'path=/mnt/second-custom,shadow:format=zfsnap2_%S_%Y-%m-%d_%H.%M.00--10y,'
                                          'vfs objects=shadow_copy2')
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[custom-0]" in cfg
            assert "path = /mnt/custom\n" in cfg
            assert "shadow:format = zfsnap_%S_%Y-%m-%d_%H.%M.00--10y\n" in cfg
            assert "vfs objects = shadow_copy\n" in cfg
            assert "[custom-1]" in cfg
            assert "path = /mnt/second-custom\n" in cfg
            assert "shadow:format = zfsnap2_%S_%Y-%m-%d_%H.%M.00--10y\n" in cfg
            assert "vfs objects = shadow_copy2\n" in cfg

        # Remove custom section
        smb.charm_config['smb-custom'] = ('path=/mnt/second-custom,shadow:format=zfsnap2_%S_%Y-%m-%d_%H.%M.00--10y,'
                                          'vfs objects=shadow_copy2')
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, 'r') as config:
            cfg = config.read()
            assert "[custom-0]" in cfg
            assert "path = /mnt/custom" not in cfg
            assert "shadow:format = zfsnap_%S_%Y-%m-%d_%H.%M.00--10y\n" not in cfg
            assert "vfs objects = shadow_copy\n" not in cfg
            assert "[custom-1]" not in cfg
            assert "path = /mnt/second-custom\n" in cfg
            assert "shadow:format = zfsnap2_%S_%Y-%m-%d_%H.%M.00--10y\n" in cfg
            assert "vfs objects = shadow_copy2\n" in cfg

        # Check that service was restarted for each save
        assert mock_check_call.call_count == 10
