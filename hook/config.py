import os


class Production:
    DEBUG = False
    TESTING = False

    JSON_AS_ASCII = False

    LOG_FOLDER = os.environ.get('LOG_FOLDER') or 'logs'
    LOG_MAX_SIZE = os.environ.get('LOG_MAX_SIZE') or 100000
    LOG_BACKUP_COUNT = os.environ.get('LOG_BACKUP_COUNT') or 5

    REPO_CONFIG_FILE = os.environ.get('REPO_CONFIG_FILE')

class Development(Production):
    DEBUG = True
    REPO_CONFIG_FILE = os.environ.get('REPO_CONFIG_FILE') or 'dev.ini'

class Testing(Production):
    TESTING = True