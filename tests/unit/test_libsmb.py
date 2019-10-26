#!/usr/bin/python3
import shutil


class TestLibsmb:
    def test_pytest(self):
        assert True

    def test_smb(self, smb):
        """ See if the smb fixture works to load charm configs """
        assert isinstance(smb.charm_config, dict)

    def test_restart(self, smb, mock_service):
        smb.restart_samba()
        assert mock_service.called_with(["restart", "smbd"])
        assert mock_service.call_count == 2

    def test_clean_example_config(self, smb):
        shutil.copyfile("./tests/unit/smb.conf", smb.config_file)
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "# Sample configuration file" in cfg
            assert ";[profiles]" in cfg
            assert "[printers]" in cfg
            assert "[print$]" in cfg
        smb.clean_example_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "# Sample configuration file" not in cfg
            assert ";[profiles]" not in cfg
            assert "[printers]" in cfg
            assert "[print$]" in cfg

    def test_update_config(self, smb, mock_check_call, mock_check_output, mock_service):
        shutil.copyfile("./tests/unit/smb.clean", smb.config_file)
        smb.reload_config()
        # Check default settings write w/o error
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[printers]" not in cfg
            assert "[print$]" not in cfg
            assert "[global]" in cfg

        # Test adding users
        smb.charm_config["smb-users"] = "ubuntu,utnubu"
        smb.update_config()
        assert "ubuntu" in smb.users
        assert "utnubu" not in smb.users

        smb.charm_config["smb-users"] = "ubuntu"
        smb.update_config()
        assert "ubuntu" in smb.users
        assert "root" not in smb.users
        assert "utnubu" not in smb.users

        # Check with one share
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "browsable = yes\n" in cfg
            assert "guest ok = yes\n" in cfg
            assert "read only = no\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = " not in cfg
            assert "force directory mode = " not in cfg
            assert "force user = " not in cfg
            assert "force group = " not in cfg
            assert "write list = " not in cfg

        # Check with multiple share
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = yes\n" in cfg
            assert "guest ok = yes\n" in cfg
            assert "read only = no\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = " not in cfg
            assert "force directory mode = " not in cfg
            assert "force user = " not in cfg
            assert "force group = " not in cfg
            assert "write list = " not in cfg

        # Check browsable
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.charm_config["smb-browsable"] = False
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = yes\n" not in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = yes\n" in cfg
            assert "read only = no\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = " not in cfg
            assert "force directory mode = " not in cfg
            assert "force user = " not in cfg
            assert "force group = " not in cfg
            assert "write list = " not in cfg

        # Check guest
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.charm_config["smb-guest"] = False
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = yes\n" not in cfg
            assert "guest ok = no\n" in cfg
            assert "read only = no\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = " not in cfg
            assert "force directory mode = " not in cfg
            assert "force user = " not in cfg
            assert "force group = " not in cfg
            assert "write list = " not in cfg

        # Check read only
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.charm_config["smb-read-only"] = True
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = no\n" in cfg
            assert "read only = no\n" not in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = " not in cfg
            assert "force directory mode = " not in cfg
            assert "force user = " not in cfg
            assert "force group = " not in cfg
            assert "write list = " not in cfg

        # Check force user
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.charm_config["smb-force-user"] = "ubuntu"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = no\n" in cfg
            assert "read only = no\n" not in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = " not in cfg
            assert "force directory mode = " not in cfg
            assert "force user = ubuntu\n" in cfg
            assert "force group = " not in cfg
            assert "write list = " not in cfg

        # Check force group
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.charm_config["smb-force-group"] = "ubuntu"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = no\n" in cfg
            assert "read only = no\n" not in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = " not in cfg
            assert "force directory mode = " not in cfg
            assert "force user = ubuntu\n" in cfg
            assert "force group = ubuntu\n" in cfg
            assert "write list = " not in cfg

        # Check force create mode
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.charm_config["smb-force-mask"] = "0666"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = no\n" in cfg
            assert "read only = no\n" not in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = 0666\n" in cfg
            assert "force directory mode = " not in cfg
            assert "force user = ubuntu\n" in cfg
            assert "force group = ubuntu\n" in cfg
            assert "write list = " not in cfg

        # Check force directory mode
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.charm_config["smb-force-dir-mask"] = "2770"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = no\n" in cfg
            assert "read only = no\n" not in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = 0666\n" in cfg
            assert "force directory mode = 2770\n" in cfg
            assert "force user = ubuntu\n" in cfg
            assert "force group = ubuntu\n" in cfg
            assert "write list = " not in cfg

        # Check write list
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test,mock2:/mnt/test-unit"
        smb.charm_config["smb-write-list"] = "ubuntu,utnubu"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "[mock2]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = no\n" in cfg
            assert "read only = no\n" not in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = 0666\n" in cfg
            assert "force directory mode = 2770\n" in cfg
            assert "force user = ubuntu\n" in cfg
            assert "force group = ubuntu\n" in cfg
            assert 'write list = "ubuntu,utnubu"\n' in cfg

        # Check removal of section
        smb.charm_config["smb-shares"] = "mock:/mnt/unit-test"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[mock]" in cfg
            assert "browsable = no\n" in cfg
            assert "guest ok = no\n" in cfg
            assert "read only = yes\n" in cfg
            assert "create mask = 0660\n" in cfg
            assert "directory mask = 0770\n" in cfg
            assert "force create mode = 0666\n" in cfg
            assert "force directory mode = 2770\n" in cfg
            assert "force user = ubuntu\n" in cfg
            assert "force group = ubuntu\n" in cfg
            assert 'write list = "ubuntu,utnubu"\n' in cfg

        # Check custom config
        smb.charm_config[
            "smb-custom"
        ] = "path=/mnt/custom,shadow:format=zfsnap_%S_%Y-%m-%d_%H.%M.00--10y,vfs objects=shadow_copy"
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
            cfg = config.read()
            assert "[custom-0]" in cfg
            assert "path = /mnt/custom\n" in cfg
            assert "shadow:format = zfsnap_%S_%Y-%m-%d_%H.%M.00--10y\n" in cfg
            assert "vfs objects = shadow_copy\n" in cfg

        # Check multiple custom configs
        smb.charm_config["smb-custom"] = (
            "path=/mnt/custom,"
            "shadow:format=zfsnap_%S_%Y-%m-%d_%H.%M.00--10y,"
            "vfs objects=shadow_copy;"
            "path=/mnt/second-custom,shadow:format=zfsnap2_%S_%Y-%m-%d_%H.%M.00--10y,"
            "vfs objects=shadow_copy2"
        )
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
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
        smb.charm_config["smb-custom"] = (
            "path=/mnt/second-custom,shadow:format=zfsnap2_%S_%Y-%m-%d_%H.%M.00--10y,"
            "vfs objects=shadow_copy2"
        )
        smb.update_config()
        smb.save_config()
        with open(smb.config_file, "r") as config:
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
        assert mock_service.called_with(["reload", "smbd"])
        assert mock_service.call_count == 30
