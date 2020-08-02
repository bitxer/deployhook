from tests.gitlab import test_evt, push_hook_master, push_hook_branch
from tests.utils import setup


def test_gitlab_push_hook_master():
    app, client = setup()
    with app.app_context():
        test_evt(client, push_hook_master, expected_status=403)

def test_gitlab_push_hook_branch():
    app, client = setup()
    with app.app_context():
        test_evt(client, push_hook_branch)
