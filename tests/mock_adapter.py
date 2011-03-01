import json
import os

import dingus

from aweber_api import AWeberUser
from aweber_api import OAuthAdapter

__all__ = ['MockAdapter']


responses = {
    'GET' : {
        '/accounts': ({}, 'accounts'),
        '/accounts/1': ({}, 'account'),
        '/accounts/1/lists': ({}, 'lists'),
        '/accounts/1?ws.op=getWebForms': ({}, 'web_forms'),
        '/accounts/1/lists?ws.start=20&ws.size=20': ({},
            'lists_page2'),
        '/accounts/1/lists/303449': ({}, 'lists/303449'),
        '/accounts/1/lists/505454': ({}, 'lists/505454'),
        '/accounts/1/lists/303449/campaigns': ({},
            'lists/303449/campaigns'),
        '/accounts/1/lists/303449/subscribers/1': ({},
            'subscribers/1'),
        '/accounts/1/lists/303449/subscribers/2': ({},
            'subscribers/2'),
        '/accounts/1/lists/505454/subscribers/3': ({},
            'subscribers/3'),
    },
    'POST' : {
        '/accounts/1/lists/303449/subscribers/1': ({'status': '201',
            'Location': '/accounts/1/lists/505454/subscribers/3'}, None),
    },
    'PATCH' : {
        '/accounts/1/lists/303449/subscribers/1': ({}, None),
        '/accounts/1/lists/303449/subscribers/2': ({'status': '403'}, None),
    },
    'DELETE' : {
        '/accounts/1/lists/303449/subscribers/1': ({}, None),
        '/accounts/1/lists/303449/subscribers/2': ({'status': '403'}, None),
    }
}

def request(self, url, method, **kwargs):
    """Return a tuple to simulate calling oauth2.Client.request."""
    (headers, file) = responses[method][url]

    if 'status' not in headers:
        # assume 200 OK if not otherwise specified
        headers['status'] = '200'

    if file is None:
        return (headers, '')
    path = os.sep.join(__file__.split(os.sep)[:-1]+['data',''])
    filename = "{0}{1}.json".format(path, file)
    data = open(filename).read()
    return (headers, data)


class MockAdapter(OAuthAdapter):
    """Mocked OAuthAdapter."""
    requests = []

    @dingus.patch('oauth2.Client.request', request)
    def request(self, method, url, data={}, response='body'):
        """Mock the oauth.Client.request method"""
        # prepare parameterized url
        if method == 'GET' and not (len(data.keys()) == 0):
            first = True
            for key in data.keys():
                if first:
                    url +='?'
                else:
                    url +='&'
                first = False
                url += key+'='+str(data[key])

        # store the request
        self.requests.append({'method' : method, 'url' : url, 'data' : data})
        return super(MockAdapter, self).request(method, url, data, response)

    def __init__(self):
        self.user = AWeberUser()
        return super(MockAdapter, self).__init__('key', 'secret', '')
