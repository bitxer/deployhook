from tests.gitlab import gitlab_evt, push_hook_master, push_hook_branch
from tests.utils import setup


def test_gitlab_push_hook_master():
    app, client = setup()
    with app.app_context():
        gitlab_evt(client, push_hook_master, expected_status=403)

def test_gitlab_push_hook_branch():
    app, client = setup()
    with app.app_context():
        gitlab_evt(client, push_hook_branch)
