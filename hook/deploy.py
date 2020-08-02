from flask import current_app as app, Blueprint, request, abort
from hook.upstream import Github, Gitlab
from hook.utils import make_response, is_valid_request, LogMessage, is_ping
from logging import getLogger

bp_deploy = Blueprint('deploy', __name__)


@bp_deploy.route('/', methods=['POST'])
def deploy():
    logger_webhook = getLogger('webhook')
    headers = request.headers
    git_upstream = None
    upstream_ip = request.remote_addr

    if 'X-Real-IP'in headers:
        upstream_ip = headers.get('X-Real-IP')
    elif 'X-Forwarded-For' in headers:
        upstream_ip = headers.get('X-Forwarded-For')

    if 'X-GitHub-Event' in headers:
        git_upstream = Github(request)
    elif 'X-Gitlab-Event' in headers:
        git_upstream = Gitlab(request)
    else:
        lm = LogMessage(status=400, upstream_ip=upstream_ip,
                        reason="Unknown Upstream")
        logger_webhook.warning(lm)
        abort(400)

    if not git_upstream.verified:
        lm = LogMessage(status=400, upstream=git_upstream.origin,
                        upstream_ip=upstream_ip, reason="Header verification failed")
        logger_webhook.warning(lm)
        abort(400)

    try:
        loc_repo = app.local_repo[git_upstream.repo]
    except KeyError:
        lm = LogMessage(status=404, upstream=git_upstream.origin, upstream_ip=upstream_ip,
                        repo=git_upstream.repo, ref=git_upstream.ref, event=git_upstream.evt, reason="Unknown Repository")
        logger_webhook.warning(lm)
        abort(404)

    if not is_valid_request(loc_repo, git_upstream):
        lm = LogMessage(status=403, upstream=git_upstream.origin, upstream_ip=upstream_ip, repo=git_upstream.repo,
                        ref=git_upstream.ref, event=git_upstream.evt, reason="Request verification failed")
        logger_webhook.warning(lm)
        abort(403)

    if is_ping(git_upstream.evt):
        lm = LogMessage(status=204, upstream=git_upstream.origin, upstream_ip=upstream_ip,
                        repo=git_upstream.repo, ref=git_upstream.ref, event=git_upstream.evt)
        logger_webhook.info(lm)
        return make_response()

    try:
        if loc_repo.deploy(git_upstream.after_hash):
            lm = LogMessage(status=204, upstream=git_upstream.origin, upstream_ip=upstream_ip,
                            repo=git_upstream.repo, ref=git_upstream.ref, event=git_upstream.evt)
            logger_webhook.info(lm)
            return make_response()
        else:
            lm = LogMessage(status=500, upstream=git_upstream.origin, upstream_ip=upstream_ip, repo=git_upstream.repo,
                            ref=git_upstream.ref, event=git_upstream.evt, reason="Unsuccessful Deployment")
            logger_webhook.error(lm)
            return make_response(500, "Unsuccessful deployment")
    except ValueError:
        lm = LogMessage(status=500, upstream=git_upstream.origin, upstream_ip=upstream_ip, repo=git_upstream.repo,
                        ref=git_upstream.ref, event=git_upstream.evt, reason="Invalid configuration for repo")
        logger_webhook.error(lm)
        return make_response(500, "Invalid configuration")
