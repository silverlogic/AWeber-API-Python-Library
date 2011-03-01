import oauth2 as oauth
import json
from urllib import urlencode

class OAuthAdapter(object):

    def __init__(self, key, secret, base):
        self.key = key
        self.secret = secret
        self.consumer = oauth.Consumer(key=self.key, secret=self.secret)
        self.api_base = base

    def _parse(self, response):
        try:
            data = json.loads(response)
            if not data or data == '':
                return response
            return data
        except:
            pass
        return response

    def request(self, method, url, data={}, response='body'):
        client = self._get_client()
        url = self._expand_url(url)
        body = self._prepare_request_body(method, url, data)
        try:
            # need a test for the next 4 lines below
            content_type = 'application/json'
            if method == 'POST':
                content_type = 'application/x-www-form-urlencoded'
            headers = {'Content-Type' : content_type}

            resp, content = client.request(url, method, body=body,
                                           headers=headers)
            if response == 'body' and isinstance(content, str):
                return self._parse(content)
            if response == 'status':
                return resp['status']
            if response == 'headers':
                return resp
        except Exception:
            # TODO: refactor this for better error handling
            pass
        return None

    def _expand_url(self, url):
        if not url[:4] == 'http':
            return '%s%s' % (self.api_base, url)
        return url

    def _get_client(self):
        token = self.user.get_highest_priority_token()
        if token:
            token = oauth.Token(token, self.user.token_secret)
            return  oauth.Client(self.consumer, token=token)
        return oauth.Client(self.consumer)

    def _prepare_request_body(self, method, url, data):
        # might need a test for the changes to this method
        if method not in ['POST', 'GET', 'PATCH'] or len(data.keys()) == 0:
            return None
        if method == 'POST':
            return urlencode(data)
        if method == 'GET':
            return '&'.join(map(lambda x: "{0}={1}".format(x, data[x]),
                                data.keys()))
        if method == 'PATCH':
            return json.dumps(data)
