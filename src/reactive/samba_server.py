from charms.reactive import (
    endpoint_from_name,
    set_state,
    when_not,
    when
)
from charmhelpers.core import (
    hookenv
)
from charmhelpers import fetch

from libsmb import SambaHelper

smb = SambaHelper()


@when_not('samba-server.installed')
def install_samba_server():
    hookenv.status_set('maintenance', 'Installing Samba')
    fetch.apt_update()
    fetch.apt_install(['samba'])
    smb.clean_example_config()
    smb.reload_config()
    smb.update_config()
    smb.save_config()
    hookenv.status_set('maintenance', 'Samba is installed')
    set_state('samba-server.installed')


@when('config.changed', 'samba-server.installed', 'layer-service-account.configured')
def update_config():
    hookenv.status_set('maintenance', 'Configuring Samba')
    smb.update_config()
    smb.save_config()
    hookenv.log("Config file written", hookenv.INFO)
    hookenv.status_set('active', 'Samba is ready')


@when('reverseproxy.departed')
def remove_proxy():
    hookenv.status_set(
        'maintenance',
        'Removing reverse proxy relation')
    hookenv.log("Removing config for: {}".format(
        hookenv.remote_unit()))

    hookenv.status_set('active', 'Samba is ready')
    hookenv.clear_flag('reverseproxy.configured')


@when('reverseproxy.ready')
@when_not('reverseproxy.configured')
def configure_proxy():
    hookenv.status_set(
        'maintenance',
        'Applying reverse proxy configuration')
    hookenv.log("Configuring reverse proxy via: {}".format(
        hookenv.remote_unit()))

    interface = endpoint_from_name('reverseproxy')
    smb.configure_proxy(interface)

    hookenv.status_set('active', 'Samba is ready')
    hookenv.set_flag('reverseproxy.configured')
