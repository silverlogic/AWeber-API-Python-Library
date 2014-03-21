import unittest2

from mock import Mock, patch, sentinel

from aweber_api import AWeberAPI
from aweber_api.base import (
    ACCESS_TOKEN_URL,
    APIException,
    API_BASE,
    AUTHORIZE_URL,
    REQUEST_TOKEN_URL,
)


class DescribeAWeberAPI(unittest2.TestCase):

    collections_map = {
        'account': ['lists', 'integrations'],
        'broadcast_campaign': ['links', 'messages', 'stats'],
        'component': [],
        'custom_field': [],
        'followup_campaign':  ['links', 'messages', 'stats'],
        'integration': [],
        'link': ['clicks'],
        'list': [
            'campaigns',
            'custom_fields',
            'subscribers',
            'web_forms',
            'web_form_split_tests',
        ],
        'message': ['opens', 'tracked_events'],
        'service-root': 'accounts',
        'subscriber': [],
        'tracked_events': [],
        'web_form': [],
        'web_form_split_test': ['components'],
    }

    @classmethod
    def setupClass(cls):
        cls.AWeberAPI = AWeberAPI(
            sentinel.consumer_key, sentinel.consumer_secret)

    def should_have_correct_api_base_url(self):
        self.assertEqual(API_BASE, 'https://api.aweber.com/1.0')

    def should_have_correct_access_token_url(self):
        self.assertEqual(
            ACCESS_TOKEN_URL, 'https://auth.aweber.com/1.0/oauth/access_token')

    def should_have_correct_authorize_url(self):
        self.assertEqual(
            AUTHORIZE_URL, 'https://auth.aweber.com/1.0/oauth/authorize')

    def should_have_correct_request_token_url(self):
        self.assertEqual(
            REQUEST_TOKEN_URL,
            'https://auth.aweber.com/1.0/oauth/request_token',
        )

    def should_have_correct_entries_in_collection_map(self):
        self.assertDictEqual(self.collections_map, AWeberAPI.collections_map)

    def should_construct_parent_url_correctly(self):
        self.assertEqual(self.AWeberAPI._construct_parent_url(
            ['', 'accounts', '1', 'lists', '1'], 1), '/accounts/1/lists')


class WhenInstantiatingAWeberAPI(unittest2.TestCase):

    @classmethod
    @patch('aweber_api.OAuthAdapter')
    @patch('aweber_api.AWeberUser')
    def setUpClass(cls, user, oauth):
        cls.AWeberUser = user
        cls.OAuthAdaptor = oauth
        cls.execute()

    @classmethod
    def execute(cls):
        cls.AWeberAPI = AWeberAPI(
            sentinel.consumer_key, sentinel.consumer_secret)

    def test_call_oAuthAdaptor(self):
        self.OAuthAdaptor.assert_called_once_with(
            sentinel.consumer_key, sentinel.consumer_secret, API_BASE)

    def test_call_AWeberUser(self):
        self.AWeberUser.assert_called_once_with()


class _basetest(unittest2.TestCase):

    @classmethod
    @patch('aweber_api.AWeberAPI.__init__', return_value=None)
    def setUpClass(cls, api):
        with patch.object(AWeberAPI, 'user') as cls.user:
            cls.configure()
            cls.execute()

    @classmethod
    def configure(cls):
        pass

    @classmethod
    def execute(cls):
        pass


class DescribePartitionURL(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI = AWeberAPI(
            sentinel.consumer_key, sentinel.consumer_secret)
        cls.AWeberAPI.url = '/accounts/1/lists/1'

    @classmethod
    def execute(cls):
        cls.url_parts = cls.AWeberAPI._partition_url()

    def should_partition_url_correctly(self):
        self.assertEqual(
            self.url_parts, ['', 'accounts', '1', 'lists', '1'])


class WhenPartitionUrlHasError(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI = AWeberAPI(
            sentinel.consumer_key, sentinel.consumer_secret)
        cls.AWeberAPI.url = '/accounts/'

    @classmethod
    def execute(cls):
        try:
            cls.url_parts = cls.AWeberAPI._partition_url()

        except (TypeError, ValueError) as exception:
            cls.exception = exception

    def should_return_none_if_number_of_parts_is_less_that_3(self):
        self.assertEqual(self.url_parts, None)


class WhenPartitionUrlProcessesNoneForURL(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI = AWeberAPI(
            sentinel.consumer_key, sentinel.consumer_secret)
        cls.AWeberAPI.url = None

    @classmethod
    def execute(cls):
        cls.url_parts = cls.AWeberAPI._partition_url()

    def should_return_none(self):
        self.assertEqual(self.url_parts, None)


class _ParseTokenBaseTest(unittest2.TestCase):

    @classmethod
    @patch('aweber_api.parse_qs')
    @patch('aweber_api.AWeberAPI.__init__', return_value=None)
    def setUpClass(cls, api, parse_qs):
        cls.AWeberAPI = AWeberAPI()
        cls.parse_qs = parse_qs

        cls.configure()
        cls.execute()

    @classmethod
    def configure(cls):
        pass

    @classmethod
    def execute(cls):
        try:
            cls.returned = cls.AWeberAPI._parse_token_response(cls.response)

        except (TypeError, ValueError) as exception:
            cls.exception = exception


class WhenParsingATokenSucceeds(_ParseTokenBaseTest):

    @classmethod
    def configure(cls):
        cls.response = Mock(spec=str)
        cls.parse_qs.return_value = {
            'oauth_token': [sentinel.auth_token],
            'oauth_token_secret': [sentinel.secret],
        }

    def should_call_parse_qs_on_the_query_string(self):
        self.parse_qs.assert_called_once_with(self.response)

    def should_return_the_expected_data(self):
        self.assertEqual(self.returned, (sentinel.auth_token, sentinel.secret))


class WhenParsingATokenWithANonStringResponse(_ParseTokenBaseTest):

    @classmethod
    def configure(cls):
        cls.response = None

    def should_raise_a_TypeError(self):
        self.assertIsInstance(self.exception, TypeError)


class WhenParsingATokenWithTheWrongResponse(_ParseTokenBaseTest):

    @classmethod
    def configure(cls):
        cls.response = ''
        cls.parse_qs.return_value = {
            'oauth': [sentinel.auth_token],
            'oauth_secret': [sentinel.secret],
        }

    def should_raise_a_ValueError(self):
        self.assertIsInstance(self.exception, ValueError)


class _GetTokenBaseTest(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI = AWeberAPI(
            sentinel.consumer_key, sentinel.consumer_secret)
        cls.adapter = Mock()
        cls.adapter.request.return_value = sentinel.response
        cls.AWeberAPI.adapter = cls.adapter
        cls.AWeberAPI._parse_token_response = Mock()
        cls.AWeberAPI._parse_token_response.return_value = (
            sentinel.access_token, sentinel.token_secret)

    @classmethod
    def execute(cls):
        pass


class DescribeGetRequestToken(_GetTokenBaseTest):

    @classmethod
    def execute(cls):
        cls.output = cls.AWeberAPI.get_request_token(
            "http://www.example.com")

    def test_make_request_with_correct_parameters(self):
        self.adapter.request.assert_called_once_with(
            'POST',
            'https://auth.aweber.com/1.0/oauth/request_token',
            {'oauth_callback': 'http://www.example.com'},
        )

    def test_must_call_parse_token_response(self):
        self.AWeberAPI._parse_token_response.assert_called_once_with(
            sentinel.response)

    def test_return_request_token(self):
        self.assertEqual(self.output[0], sentinel.access_token)

    def test_return_request_token_secret(self):
        self.assertEqual(self.output[1], sentinel.token_secret)


class DescribeGetAccessToken(_GetTokenBaseTest):

    @classmethod
    def execute(cls):
        cls.output = cls.AWeberAPI.get_access_token()

    def should_make_request_with_correct_parameters(self):
        self.adapter.request.assert_called_once_with(
            'POST',
            'https://auth.aweber.com/1.0/oauth/access_token',
            {'oauth_verifier': self.user.verifier},
        )

    def should_call_parse_token_response(self):
        self.AWeberAPI._parse_token_response.assert_called_once_with(
            sentinel.response)

    def should_return_request_access_token(self):
        self.assertEqual(self.output[0], sentinel.access_token)

    def should_return_request_access_token_secret(self):
        self.assertEqual(self.output[1], sentinel.token_secret)


class _ParseAuthorizationBaseTest(unittest2.TestCase):

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
        try:
            cls.returned = cls.AWeberAPI.parse_authorization_code(
                cls.auth_code)

        except APIException as exception:
            cls.exception = exception


class WhenGettingAPIKeysWithBadAuthorizationCode(_ParseAuthorizationBaseTest):

    @classmethod
    def configure(cls):
        cls.adapter = Mock()
        cls.adapter.request = Mock()
        cls.adapter.request.return_value = sentinel.response
        cls.consumer_key = sentinel.consumer_key
        cls.AWeberAPI.adapter = cls.adapter
        cls.auth_code = "1|2|3"

    def should_raise_APIException(self):
        self.assertIsInstance(self.exception, APIException)


class DescribeGetAccount(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI = AWeberAPI(
            sentinel.consumer_key, sentinel.consumer_secret)
        cls.adapter = Mock()
        cls.adapter.request.return_value = {
            'entries': [{'self_link': ''}], 'start': 0, 'total_size': 1}
        cls.AWeberAPI.adapter = cls.adapter
        cls.AWeberAPI._read_response = Mock()
        cls.AWeberAPI._read_response.return_value = [sentinel.response]

    @classmethod
    def execute(cls):
        cls.returned = cls.AWeberAPI.get_account(
            sentinel.access_token, sentinel.token_secret)

    def should_make_get_accounts_request(self):
        self.AWeberAPI.adapter.request.assert_called_once_with(
            'GET', '/accounts')

    def should_call_read_response(self):
        self.AWeberAPI._read_response.assert_called_once_with(
            '/accounts', self.adapter.request.return_value)


class DescribeLoadFromURL(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI = AWeberAPI(
            sentinel.consumer_key, sentinel.consumer_secret)
        cls.adapter = Mock()
        cls.adapter.request.return_value = {
            'entries': [{'self_link': ''}], 'start': 0, 'total_size': 1}
        cls.AWeberAPI.adapter = cls.adapter
        cls.AWeberAPI._read_response = Mock()
        cls.AWeberAPI._read_response.return_value = ''

    @classmethod
    def execute(cls):
        cls.returned = cls.AWeberAPI.load_from_url("http://www.example.com")

    def should_make_get_request_for_url(self):
        self.AWeberAPI.adapter.request.assert_called_once_with(
            'GET', 'http://www.example.com')

    def should_call_read_response(self):
        self.AWeberAPI._read_response.assert_called_once_with(
            'http://www.example.com', self.adapter.request.return_value)
