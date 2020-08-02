from hook import init_app

def setup():
    app = init_app(config="hook.config.Testing")
    with app.app_context():
        return app, app.test_client()