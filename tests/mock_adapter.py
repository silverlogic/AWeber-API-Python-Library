from aweber_api import AWeberUser
import json
import os

class MockAdapter(object):

    def __init__(self):
        self.user = AWeberUser()

    request_paths = {
        'GET' : {
            '/accounts'                                : 'accounts',
            '/accounts/1'                              : 'account',
            '/accounts/1/lists'                        : 'lists',
            '/accounts/1?ws.op=getWebForms'            : 'web_forms',
            '/accounts/1/lists?ws.start=20&ws.size=20' : 'lists_page2',
            '/accounts/1/lists/303449'                 : 'lists/303449',
            '/accounts/1/lists/303449/campaigns'       : 'lists/303449/campaigns',
            '/accounts/1/lists/303449/subscribers/1'   : 'subscribers/1',
            '/accounts/1/lists/303449/subscribers/2'   : 'subscribers/2'
        },
        'PATCH' : {
            '/accounts/1/lists/303449/subscribers/1'   : '200',
            '/accounts/1/lists/303449/subscribers/2'   : '403'
        },
        'DELETE' : {
            '/accounts/1/lists/303449/subscribers/1'   : '200',
            '/accounts/1/lists/303449/subscribers/2'   : '403'
        }
    }

    requests = []

    def request(self, method, url, data={}, response=False):
        if method == 'GET' and not (len(data.keys()) == 0):
            first = True
            for key in data.keys():
                if first:
                    url +='?'
                else:
                    url +='&'
                first = False
                url += key+'='+str(data[key])

        if not url in self.request_paths[method]:
            return ''
        self.requests.append({'method' : method, 'url' : url, 'data' : data})

        if not response:
            path = "{0}{1}.json".format(self.data_dir,
                                        self.request_paths[method][url])

            return json.load(open(path))
        if response == 'status':
            return self.request_paths[method][url]

    @property
    def data_dir(self):
        s = os.sep
        return s.join(__file__.split(s)[:-1]+['data',''])
