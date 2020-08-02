from git import Repo as GitRepo
from flask import current_app as app
from configparser import ConfigParser
from os.path import isfile, isabs
from subprocess import run


class LocalRepos:
    def __init__(self, config_path):
        self.repo = {}
        config = ConfigParser()
        config.read(config_path)
        for section in config.sections():
            repo = Repo(**config[section])
            self.repo[repo.name] = repo

    def __getitem__(self, key):
        return self.repo[key]

    def __setitem__(self, key, value):
        if key in self.repo:
            raise TypeError(
                "'LocalRepos' object does not support item assignment")

    def __repr__(self):
        return str(self.repo.keys())


class Repo:
    def __init__(self, name, repopath, secret, sshkey='', action='default', branch='master', script=None):
        self.title = name + branch
        self.name = name
        self.repo = GitRepo(repopath)
        action = action.lower()
        if action in ['default', 'script']:
            self.action = action
        else:
            raise ValueError('action for {} is not supported'.format(name))

        if action == 'script':
            if script is None:
                raise ValueError('Script not specified for {}'.format(name))
            elif not app.config['TESTING'] and not isabs(script):
                raise ValueError(
                    'Script for {} is not a absolute path'.format(name))

        self.script = script

        if sshkey != '' and isfile(sshkey):
            self.ssh_cmd = 'ssh -i {}'.format(sshkey)
        else:
            self.ssh_cmd = 'ssh'

        self.branch = branch
        self.repo.git.checkout('-B', self.branch)
        self.__update()

        self.secret = secret

    def __update(self):
        with self.repo.git.custom_environment(GIT_SSH_COMMAND=self.ssh_cmd):
            self.repo.git.pull('origin', self.branch)

    def deploy(self, expected_commit=None):
        self.__update()
        if self.action == 'default':
            return str(self.repo.head.commit) == expected_commit
        elif self.action == 'script':
            try:
                run(self.script, cwd=self.repo.working_dir, check=True)
                return True
            except Exception:
                return False
        else:
            raise ValueError
