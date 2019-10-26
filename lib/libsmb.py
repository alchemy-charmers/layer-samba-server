import fileinput
from subprocess import CalledProcessError, check_call, check_output

from charmhelpers.core import hookenv
from charmhelpers.core.host import pwgen, service
from configobj import ConfigObj


class SambaHelper:
    def __init__(self):
        self.charm_config = hookenv.config()
        self.config_file = "/etc/samba/smb.conf"
        self.smb_config = ConfigObj(self.config_file)
        self.users = []

    def restart_samba(self):
        service("restart", "smbd")
        service("restart", "nmbd")

    def reload_samba(self):
        service("reload", "smbd")
        service("reload", "nmbd")

    def reload_config(self):
        self.smb_config = ConfigObj(self.config_file)

    def save_config(self):
        hookenv.log("Writing config file {}".format(self.config_file), "DEBUG")
        self.smb_config.write()
        self.reload_samba()

    def clean_example_config(self):
        for line in fileinput.input(self.config_file, inplace=True):
            if line.startswith("#") or line.startswith(";"):
                continue
            if "\n" == line:
                continue
            print(line, end="")

    def ensure_users(self, users):
        self.update_users()
        # add users here, call add user helper as needed
        userlist = users.split(",")
        if userlist and len(userlist) > 0:
            for user in userlist:
                # check if user is in local password database, create
                # if not already there
                if user not in self.users:
                    self.add_user(user)
            # if so, lets add them to smbpasswd
        # check smbpasswd list for users that are not in provided config
        for smbuser in self.users:
            if smbuser not in userlist:
                # we found an orphan, set phasers to delete
                self.remove_user(smbuser)

    def update_users(self):
        try:
            sambatool = check_output(["samba-tool", "user", "list"])
        except CalledProcessError:
            hookenv.log("Error getting users", "ERROR")
            return False
        else:
            self.users = sambatool.split("\n")

    def add_user(self, user):
        try:
            sambatool = check_output(["samba-tool", "user", "getpassword", user])
        except CalledProcessError:
            hookenv.log(
                "Error getting password for user {} in smbpasswd".format(user), "ERROR"
            )
            return False
        else:
            return sambatool

    def get_password(self, user):
        try:
            sambatool = check_output(["samba-tool", "user", "getpassword", user])
        except CalledProcessError:
            hookenv.log(
                "Error getting password for user {} in smbpasswd".format(user), "ERROR"
            )
            return False
        else:
            return sambatool

    def set_password(self, user, password):
        # if password is empty or false, auto-generate
        if not password:
            password = pwgen()
        # run samba-tool
        try:
            check_call(
                [
                    "samba-tool",
                    "user",
                    "setpassword",
                    user,
                    "--newpassword={}".format(password),
                ]
            )
        except CalledProcessError:
            hookenv.log(
                "Error setting password for user {} in smbpasswd".format(user), "ERROR"
            )
            return False
        else:
            return True

    def update_config(self):
        hookenv.log("Updating configuration", "DEBUG")
        if self.charm_config["smb-users"]:
            hookenv.log(
                "Processing users: {}".format(self.charm_config["smb-users"]), "DEBUG"
            )
            self.ensure_users(self.charm_config["smb-users"])
        if self.charm_config["smb-shares"]:
            hookenv.log(
                "Processing shares: {}".format(self.charm_config["smb-shares"]), "DEBUG"
            )
            for entry in self.charm_config["smb-shares"].split(","):
                if ":" in entry:
                    share, path = entry.split(":")
                    self.smb_config[share] = {}
                    self.smb_config[share]["path"] = path

                    if self.charm_config["smb-browsable"]:
                        self.smb_config[share]["browsable"] = "yes"
                    else:
                        self.smb_config[share]["browsable"] = "no"

                    if self.charm_config["smb-guest"]:
                        self.smb_config[share]["guest ok"] = "yes"
                    else:
                        self.smb_config[share]["guest ok"] = "no"

                    if self.charm_config["smb-read-only"]:
                        self.smb_config[share]["read only"] = "yes"
                    else:
                        self.smb_config[share]["read only"] = "no"

                    if self.charm_config["smb-force-mask"]:
                        self.smb_config[share]["force create mode"] = self.charm_config[
                            "smb-force-mask"
                        ]

                    if self.charm_config["smb-force-dir-mask"]:
                        self.smb_config[share][
                            "force directory mode"
                        ] = self.charm_config["smb-force-dir-mask"]

                    if self.charm_config["smb-force-user"]:
                        self.smb_config[share]["force user"] = self.charm_config[
                            "smb-force-user"
                        ]

                    if self.charm_config["smb-force-group"]:
                        self.smb_config[share]["force group"] = self.charm_config[
                            "smb-force-group"
                        ]

                    if self.charm_config["smb-write-list"]:
                        self.smb_config[share]["write list"] = self.charm_config[
                            "smb-write-list"
                        ]

                    self.smb_config[share]["create mask"] = self.charm_config[
                        "smb-create-mask"
                    ]
                    self.smb_config[share]["directory mask"] = self.charm_config[
                        "smb-dir-mask"
                    ]

        if self.charm_config["smb-custom"]:
            for num, share in enumerate(self.charm_config["smb-custom"].split(";")):
                share_name = "custom-" + str(num)
                self.smb_config[share_name] = {}
                for setting in share.split(","):
                    key, value = setting.split("=")
                    self.smb_config[share_name][key] = value
        for section in self.smb_config.keys():
            sections = ["global"]
            if self.charm_config["smb-shares"]:
                for entry in self.charm_config["smb-shares"].split(","):
                    share, path = entry.split(":")
                    sections.append(share)
            if self.charm_config["smb-custom"]:
                sections.extend(
                    [
                        "custom-{}".format(i)
                        for i, dummy in enumerate(
                            self.charm_config["smb-custom"].split(";")
                        )
                    ]
                )
            if section not in sections:
                del self.smb_config[section]
