from unittest2 import TestCase

from mock import Mock, patch, sentinel
from mock_adapter import MockAdapter

from aweber_api import (
    ACCESS_TOKEN_URL,
    AUTHORIZE_URL,
    AWeberAPI,
    AWeberEntry,
    AWeberUser,
    REQUEST_TOKEN_URL,
)


class _BaseTest(TestCase):

    @classmethod
    @patch('aweber_api.AWeberAPI.__init__', return_value=None)
    def setUpClass(cls, api):
        with patch.object(AWeberAPI, 'user') as cls.user:
            cls.AWeberAPI = AWeberAPI(
                sentinel.consumer_key, sentinel.consumer_secret)
            cls.configure()
            cls.execute()

    @classmethod
    def configure(cls):
        pass

    @classmethod
    def execute(cls):
        pass


class _RequestTokenBaseTest(_BaseTest):

    @classmethod
    def execute(cls):
        cls.token, cls.secret = cls.AWeberAPI.get_request_token(
            'http://localhost/demo')


class WhenGettingARequestToken(_RequestTokenBaseTest):

    @classmethod
    def configure(cls):
        cls.response = "oauth_token=1234&oauth_token_secret=abcd"
        cls.AWeberAPI.adapter = Mock()
        cls.AWeberAPI.adapter.user = AWeberUser()
        cls.AWeberAPI.adapter.request = Mock()
        cls.AWeberAPI.adapter.request.return_value = cls.response

    def should_get_request_token(self):
        self.assertEqual(self.token, '1234')

    def should_get_request_token_secret(self):
        self.assertEqual(self.secret, 'abcd')

    def should_set_up_user_access_token(self):
        self.assertEqual(self.user.request_token, self.token)

    def should_set_up_user_token_secret(self):
        self.assertEqual(self.user.token_secret, self.secret)


class WhenGettingARequestTokenGetURL(_RequestTokenBaseTest):

    @classmethod
    def configure(cls):
        cls.response = "oauth_token=1234&oauth_token_secret=abcd"
        cls.AWeberAPI.adapter = Mock()
        cls.AWeberAPI.adapter.user = AWeberUser()
        cls.AWeberAPI.adapter.request = Mock()
        cls.AWeberAPI.adapter.request.return_value = cls.response

    def test_should_have_authorize_url(self):
        self.AWeberAPI.get_request_token(
            'http://localhost/demo')
        self.assertEqual(
            self.AWeberAPI.authorize_url,
            "{0}?oauth_token={1}".format(AUTHORIZE_URL, self.token),
        )


class WhanGettingARequestTokenAndPassingArgsToRequest(_RequestTokenBaseTest):

    @classmethod
    def configure(cls):
        cls.response = "oauth_token=cheeseburger&oauth_token_secret=hotdog"
        cls.AWeberAPI.adapter = Mock()
        cls.AWeberAPI.adapter.user = AWeberUser()
        cls.AWeberAPI.adapter.request = Mock()
        cls.AWeberAPI.adapter.request.return_value = cls.response
        cls.called = False

        def _request(method, url, params=None):
            cls._request_method = method
            cls._request_url = url
            cls._request_params = params

            cls.called = True
            return cls.response

        cls.AWeberAPI.adapter.request = _request

    @classmethod
    def execute(cls):
        cls.access_token, cls.token_secret = cls.AWeberAPI.get_request_token(
            'http://localhost/demo')

    def should_pass_args_to_request(self):
        self.assertTrue(self.called, 'Called _request')

    def should_pass_method_to_request(self):
        self.assertEqual(self._request_method, 'POST')

    def should_pass_url_to_request(self):
        self.assertEqual(self._request_url, REQUEST_TOKEN_URL)

    def should_pass_params_to_request(self):
        self.assertEqual(
            self._request_params['oauth_callback'], 'http://localhost/demo')


class WhenGettingAnAccessToken(_BaseTest):

    @classmethod
    def configure(cls):
        cls.response = "oauth_token=cheeseburger&oauth_token_secret=hotdog"
        cls.AWeberAPI.adapter = Mock()
        cls.AWeberAPI.adapter.user = AWeberUser()
        cls.AWeberAPI.adapter.request = Mock()
        cls.AWeberAPI.adapter.request.return_value = cls.response

        cls.AWeberAPI.user.request_token = '1234'
        cls.AWeberAPI.user.token_secret = 'abcd'
        cls.AWeberAPI.user.verifier = '234a35a1'

    @classmethod
    def execute(cls):
        cls.access_token, cls.token_secret = cls.AWeberAPI.get_access_token()

    def should_use_correct_access_token(self):
        self.assertEqual(self.access_token, 'cheeseburger')

    def should_use_correct_token_secret(self):
        self.assertEqual(self.token_secret, 'hotdog')

    def should_set_up_user_access_token(self):
        self.assertEqual(self.user.access_token, self.access_token)

    def should_set_up_user_token_secret(self):
        self.assertEqual(self.user.token_secret, self.token_secret)


class WhanGettingAnAccessTokenAndPassingArgsToRequest(_BaseTest):

    @classmethod
    def configure(cls):
        cls.response = "oauth_token=cheeseburger&oauth_token_secret=hotdog"
        cls.AWeberAPI.adapter = Mock()
        cls.AWeberAPI.adapter.user = AWeberUser()
        cls.AWeberAPI.adapter.request = Mock()
        cls.AWeberAPI.adapter.request.return_value = cls.response

        cls.AWeberAPI.user.request_token = '1234'
        cls.AWeberAPI.user.token_secret = 'abcd'
        cls.AWeberAPI.user.verifier = '234a35a1'
        cls.called = False

        def _request(method, url, params=None):
            cls._request_method = method
            cls._request_url = url
            cls._request_params = params

            cls.called = True
            return cls.response

        cls.AWeberAPI.adapter.request = _request

    @classmethod
    def execute(cls):
        cls.access_token, cls.token_secret = cls.AWeberAPI.get_access_token()

    def should_pass_args_to_request(self):
        self.assertTrue(self.called, 'Called _request')

    def should_pass_method_to_request(self):
        self.assertEqual(self._request_method, 'POST')

    def should_pass_url_to_request(self):
        self.assertEqual(self._request_url, ACCESS_TOKEN_URL)

    def should_pass_params_to_request(self):
        self.assertEqual(
            self._request_params['oauth_verifier'], self.user.verifier)


class WhenGettingAnAccount(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.access_token = '1234'
        cls.token_secret = 'abcd'

    @classmethod
    def execute(cls):
        cls.account = cls.AWeberAPI.get_account(
            sentinel.access_token, sentinel.token_secret)

    def should_return_account_type_as_entry(self):
        self.assertEqual(type(self.account), AWeberEntry)

    def should_return_correct_account_id(self):
        self.assertEqual(self.account.id, 1)

    def should_return_an_account_type(self):
        self.assertEqual(self.account.type, 'account')
