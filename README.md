# deployhook


## Repo Config File
The application makes use of INI config files. The following table details the keys available and their details
| Attribute | Description                                                         | Required |
|-----------|---------------------------------------------------------------------|:--------:|
| name      | Full repo name of the directory (e.g. bitxer/deployhook)            | YES      |
| repopath  | Local repo path on the filesystem                                   | YES      |
| secret    | Secret used to verify requests                                      | YES      |
| branch    | Git branch to trigger the action [Default: master]                  | NO       |
| action    | Action to trigger [default/script]                                  | NO       |
| script    | Absolute path to script to trigger if the action is script          | NO       |
| sshkey    | SSH deploy key to pull the repository                               | NO       |


### Example Config
The following are examples of sections within the configuration file

#### Default Config
The default action is a git pull to update the branch in the local repo
```
[bitxer/deployhook]
name = bitxer/deployhook
repopath = /path/to/repo
secret = secret
sshkey = /path/to/script.pem
branch = master
```

#### Script Config
```
[bitxer/deployhook]
name = bitxer/deployhook
repopath = /path/to/repo
secret = secret
branch = branch1
action = script
script = /path/to/script
```