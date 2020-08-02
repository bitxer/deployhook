import logging, os
from flask import Flask
from logging.handlers import RotatingFileHandler
from hook.repo import LocalRepos

def h_badrequest(e):
    return 'Bad Request', 400


def init_app(config="hook.config.Production"):
    app = Flask(__name__)

    with app.app_context():
        app.config.from_object(config)
        app.local_repo = LocalRepos(app.config['REPO_CONFIG_FILE'])
        fhandler = RotatingFileHandler(os.path.join(app.config['LOG_FOLDER'], 'webhook.log'), app.config['LOG_MAX_SIZE'], app.config['LOG_BACKUP_COUNT'])
        fhandler.setLevel(logging.INFO)
        fhandler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))

        logger_webhook = logging.getLogger('webhook')
        logger_webhook.setLevel(logging.INFO)
        logger_webhook.addHandler(fhandler)
    
        from hook.deploy import bp_deploy
        app.register_blueprint(bp_deploy)

        app.register_error_handler(400, h_badrequest)
        app.register_error_handler(405, h_badrequest)

    return app
