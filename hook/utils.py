from flask import jsonify

class LogMessage():
    def __init__(self, status, upstream='UNKNOWN', upstream_ip='UNKNOWN', repo='UNKNOWN', ref='UNKNOWN', event='UNKNOWN', reason=None):
        self.upstream = upstream
        self.upstream_ip = upstream_ip
        self.repo = repo
        self.ref = ref
        self.event = event
        self.status = status
        self.reason = reason

    def __str__(self):
        return 'upstream={} upstream_ip={} repo={} ref={} event={} status={} reason={}'.format(
            self.upstream, self.upstream_ip, self.repo, self.ref, self.event, self.status, self.reason)


def is_ping(evt):
    return evt == 'PING'

def is_valid_request(loc_repo, git_upstream):
    is_valid_secret = isinstance(loc_repo.secret, type(None)) or git_upstream.verify(loc_repo.secret)
    try:
        is_valid_branch = git_upstream.ref[1] == 'heads' and git_upstream.ref[2] == loc_repo.branch
    except IndexError:
        return is_valid_secret and is_ping(git_upstream.evt)
    return is_valid_secret and is_valid_branch


def make_response(status_code=204, message=''):
    response = jsonify({"message": message})
    response.status_code = status_code
    return response
