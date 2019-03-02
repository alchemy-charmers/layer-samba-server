# Samba 

Describe the intended usage of this charm and anything unique about how this
charm relates to others here.

This README will be displayed in the Charm Store, it should be either Markdown
or RST. Ideal READMEs include instructions on how to use the charm, expected
usage, and charm features that your audience might be interested in. For an
example of a well written README check out Hadoop:
http://jujucharms.com/charms/precise/hadoop

Use this as a Markdown reference if you need help with the formatting of this
README: http://askubuntu.com/editing-help

This charm provides [service][]. Add a description here of what the service
itself actually does.

Also remember to check the [icon guidelines][] so that your charm looks good
in the Juju GUI.

# Usage

juju deploy cs:~pirate-charmers/samba-server

## Known Limitations and Issues

 - Passwords can not be set using charm configuration, and must be set
   on each unit, using the `set-user-pass` action

# Configuration

`smb-shares`

A Comma separated list of folders to share. Optionally, flags can be set on each share by separating with commas - e.g. /mnt/storage:ro:guest:browsable:write=ubuntu to configure a storage share, that is read only, guest accessible and browsable, and only writable by the ubuntu user.

`smb-browsable`

Shares are browsable by default, but can be disabled by setting this to false.

`smb-guest`

The configured shares allow guest access by default, but this can be disabled by setting this to false.

`smb-read-only`
The configured shares are not read only by default, but can be configured as read only by setting this to true.

`smb-create-mask`

The default mask applied to created files. Defaults to `0660`

`smb-dir-mask`

The default mask applied to created directories. Defaults to `0770`

`smb-users`

A comma separated list of users to create in Samba's user database. Passwords will be automatically generated, and will need to be set to something known using the `set-passwd` action. No users are created by default.

`smb-force-group`
`smb-force-user'

For the local UNIX group and user to be used for file operations on backend storage respectively. Optional, will not be set if these settings are unset.

`smb-force-dir-mask`
`smb-force-mask`

If set, forces the create mode for new directories or files created by Samba, respectively. This is OR'd with smb-dir-mask and smb-create-mask by Samba when new files are created to determine the final directory of file mask.

`smb-write-list`

If configured, the provided comma separated list of users will be able to write to shares. These users need to exist in the samba user database, which can be configured with the `smb-users` setting

`smb-custom`

Raw configuration to append to `smb.conf`, provide key=value comma separated keys. Use semicolon to separate shares

# Contact Information

This charm is written and maintained by the [pirate-charmers](https://github.com/pirate-charmers) group.

## Samba

  - [Upstream website](https://samba.org)
  - [Upstream bug tracker](https://bugzilla.samba.org/)
  - [Charm store](https://jujucharms.com/u/pirate-charmers/samba-server)
  - [Charm GitHub](https://github.com/pirate-charmers/layer-samba-server)
