from tests.github import test_evt, ping, push_master, push_branch
from tests.utils import setup


def test_github_ping():
    app, client = setup()
    with app.app_context():
        test_evt(client, ping)


def test_github_push_master():
    app, client = setup()
    with app.app_context():
        test_evt(client, push_master)


def test_github_push_branch():
    app, client = setup()
    with app.app_context():
        test_evt(client, push_branch, expected_status=403)
