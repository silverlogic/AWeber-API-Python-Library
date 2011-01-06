import oauth2 as oauth
import json

class OAuthAdapter(object):

    def __init__(self, key, secret, base):
        self.key = key
        self.secret = secret
        self.consumer = oauth.Consumer(key=self.key, secret=self.secret)
        self.api_base = base
        self.debug = False

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
        if self.debug:
            print " *** {0}: {1} ".format(method, url)
        try:
            headers = {'Content-Type' : 'application/json'}
            resp, content = client.request(url, method, body=body,
                                           headers=headers)
            if self.debug:
                print resp
                print content
            if response == 'body' and type(content) == str:
                return self._parse(content)
            if response == 'status':
                return resp['status']
        except e:
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
        if len(data.keys()) == 0 or method not in ['GET', 'PATCH']:
            return None

        if method == 'GET':
            return '&'.join(map(lambda x: "{0}={1}".format(x, data[x]),
                                data.keys()))
        if method == 'PATCH':
            return json.dumps(data)
