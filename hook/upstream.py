import hmac
import json
from hashlib import sha1


class Upstream:
    origin = None
    _authorised_evt = {}
    _evt_header = None
    _authorised_ua = None
    _authorised_type = 'application/json'
    verified = True

    def __init__(self, request):
        self.request = request

        if not self._verify_headers():
            self.verified = False
        else:
            evt = request.headers.get(self._evt_header).lower().strip()
            self.evt = self._authorised_evt[evt]
            self.repo = self._get_repo_name()
            self.ref = self._get_ref()
            self.after_hash = self._get_after()

    def _verify_headers(self):
        headers = self.request.headers
        return headers.get(self._evt_header).lower() in self._authorised_evt and \
               headers.get('Content-Type') == self._authorised_type and \
               headers.get('User-Agent', '').startswith(self._authorised_ua)

    def _get_repo_name(self):
        return ''

    def _get_request_body(self):
        data = self.request.data.decode()
        data = data.replace('\r\n', '')
        data = data.replace('\n', '')
        return json.loads(data)

    def _get_ref(self):
        return self._get_request_body().get('ref', '').split('/')
    
    def _get_after(self):
        return self._get_request_body().get('after', '')


class Github(Upstream):
    origin = 'Github'
    _authorised_evt = {'ping': 'PING', 'push': 'PUSH'}
    _evt_header = 'X-GitHub-Event'
    _authorised_ua = 'GitHub-Hookshot/'
    __signature_header = 'X-Hub-Signature'

    def _get_repo_name(self):
        return self._get_request_body()['repository']['full_name'].strip().lower()

    def verify(self, secret):
        try:
            signature = self.request.headers[self.__signature_header].split('=')
        except KeyError:
            return False

        signature = str(signature[1].strip())
        secret = bytes(str(secret), 'utf-8')
        computed = hmac.new(secret, self.request.data, sha1).hexdigest()
        return hmac.compare_digest(signature, str(computed))

class Gitlab(Upstream):
    origin = 'Gitlab'
    _authorised_evt = {'push hook': 'PUSH'}
    _evt_header = 'X-Gitlab-Event'
    _authorised_ua = ''
    __secret_header = 'X-Gitlab-Token'

    def _get_repo_name(self):
        return self._get_request_body()['project']['path_with_namespace'].strip().lower()

    def _verify_headers(self):
        headers = self.request.headers
        return headers.get(self._evt_header).lower() in self._authorised_evt and \
               headers.get('Content-Type') == self._authorised_type

    def verify(self, secret):
        try:
            return self.request.headers[self.__secret_header].strip() == secret
        except KeyError:
            return False
