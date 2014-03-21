from collections import Iterable
from json import dumps
from unittest2 import TestCase

from mock import Mock, patch, sentinel
from mock_adapter import MockAdapter

from aweber_api import AWeberAPI, AWeberCollection, AWeberEntry
from aweber_api.base import API_BASE, APIException


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


class TestAWeberCollection(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def execute(cls):
        cls.lists = cls.AWeberAPI.load_from_url('/accounts/1/lists')

    def should_return_collection_of_lists(self):
        self.assertTrue(type(self.lists), AWeberCollection)

    def should_be_able_to_iterate_on_collection(self):
        self.assertIsInstance(self.lists, Iterable)

    def should_have_correct_number_of_items_in_collection(self):
        self.assertTrue(len(self.lists), 24)

    def should_be_able_get_each_item_entry_via_offset(self):
        for i in range(0, 23):
            selected_list = self.lists[i]
            self.assertEqual(type(selected_list), AWeberEntry)

    def should_be_able_get_each_item_type_via_offset(self):
        for i in range(0, 23):
            selected_list = self.lists[i]
            self.assertEqual(selected_list.type, 'list')


class TestAWeberCollectionCreateEntry(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []
        cls.base_url = '/accounts/1'

    @classmethod
    def execute(cls):
        cls.lists = cls.AWeberAPI.load_from_url('/accounts/1/lists')
        cls.account = cls.AWeberAPI.load_from_url(cls.base_url)
        cls.subscribers = cls.account.findSubscribers(email='joe@example.com')

    def test_should_create_entries_with_correct_url(self):
        for subscriber in self.subscribers:
            self.assertEqual(
                subscriber.url, subscriber.self_link.replace(API_BASE, ''))


class TestAWeberCollectionMethodGetById(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def execute(cls):
        cls.lists = cls.AWeberAPI.load_from_url('/accounts/1/lists')
        cls.list = cls.lists.get_by_id(303449)

    def test_get_by_id_returns_entry(self):
        self.assertEqual(type(self.list), AWeberEntry)

    def test_get_by_id_returns_correct_entry_type(self):
        self.assertEqual(self.list.type, 'list')

    def test_get_by_id_returns_correct_entry_id(self):
        self.assertEqual(self.list.id, 303449)


class TestAWeberCollectionFindMethod(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def execute(cls):
        cls.base_url = '/accounts/1/lists/303449/subscribers'
        cls.subscriber_collection = cls.AWeberAPI.load_from_url(cls.base_url)
        cls.AWeberAPI.adapter.requests = []
        cls.subscribers = cls.subscriber_collection.find(
            email='joe@example.com')
        cls.request = cls.AWeberAPI.adapter.requests[0]

    def should_return_a_collection(self):
        self.assertIsInstance(self.subscribers, AWeberCollection)

    def should_return_correct_number_of_items_in_collection(self):
        self.assertEqual(len(self.subscribers), 1)

    def should_return_self_link(self):
        self.assertEqual(self.subscribers[0].self_link, (
            'https://api.aweber.com/1.0/accounts/1/lists/303449/subscribers'
            '/50205517'))

    def should_return_request_url(self):
        self.assertEqual(
            self.request['url'],
            '{0}?ws.op=find&email=joe%40example.com'.format(self.base_url)
        )


class TestAWeberCollectionFindMethodHandleErrors(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def execute(cls):
        cls.base_url = '/accounts/1/lists/303449/subscribers'
        cls.subscriber_collection = cls.AWeberAPI.load_from_url(cls.base_url)

    def test_find_should_handle_errors(self):
        self.assertRaises(
            APIException, self.subscriber_collection.find, name='joe')


class WhenCreatingCustomFieldsFails(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []
        cls.cf_url = '/accounts/1/lists/505454/custom_fields'

    @classmethod
    def execute(cls):
        cls.cf = cls.AWeberAPI.load_from_url(cls.cf_url)

    def test_should_raise_exception(self):
        self.assertRaises(APIException, self.cf.create, name='Duplicate Name')


class WhenCreatingCustomFields(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []
        cls.cf_url = '/accounts/1/lists/303449/custom_fields'

    @classmethod
    def execute(cls):
        cls.cf = cls.AWeberAPI.load_from_url(cls.cf_url)
        cls.AWeberAPI.adapter.requests = []
        cls.resp = cls.cf.create(name='Wedding Song')

    def should_return_new_resource_entry_object(self):
        self.assertTrue(isinstance(self.resp, AWeberEntry))

    def should_return_new_resource_url(self):
        self.assertEqual(
            self.resp.url, '/accounts/1/lists/303449/custom_fields/2')

    def should_return_correct_resource_param_color(self):
        self.assertEqual(self.resp.name, u'COLOR')

    def should_return_correct_resource_param_isupdatable(self):
        self.assertEqual(self.resp.is_subscriber_updateable, True)

    def should_return_correct_resource_id(self):
        self.assertEqual(self.resp.id, 2)


class TestCreateMethod(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []
        cls.url = '/accounts/1/lists/303449/any_collection'

    @classmethod
    def execute(cls):
        cls.any_collection = cls.AWeberAPI.load_from_url(cls.url)
        cls.AWeberAPI.adapter.requests = []
        cls.resp = cls.any_collection.create(
            a_string='Bob', a_dict={'Color': 'blue'}, a_list=['apple'])
        cls.create_req = cls.AWeberAPI.adapter.requests[0]
        cls.get_req = cls.AWeberAPI.adapter.requests[1]

    def should_make_request_with_correct_parameters(self):
        expected_params = {
            'ws.op': 'create',
            'a_string': 'Bob',
            'a_dict': dumps({'Color': 'blue'}),
            'a_list': dumps(['apple']),
        }
        self.assertEqual(self.create_req['data'], expected_params)

    def should_make_two_requests(self):
        self.assertEqual(len(self.AWeberAPI.adapter.requests), 2)

    def should_have_requested_create_on_cf(self):
        self.assertEqual(self.create_req['url'], self.any_collection.url)

    def should_have_requested_create_with_post(self):
        self.assertEqual(self.create_req['method'], 'POST')

    def should_refresh_created_resource(self):
        self.assertEqual(self.get_req['method'], 'GET')

    def should_refresh_created_resource_get_url(self):
        self.assertEqual(
            self.get_req['url'], '/accounts/1/lists/303449/any_collection/1')


class TestParentEntryMethod(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []
        cls.url = '/accounts/1/lists/303449/any_collection'

    @classmethod
    def execute(cls):
        cls.lists = cls.AWeberAPI.load_from_url('/accounts/1/lists')
        cls.accounts = cls.AWeberAPI.load_from_url('/accounts')
        cls.custom_fields = cls.AWeberAPI.load_from_url(
            '/accounts/1/lists/303449/custom_fields')
        cls.lists_entry = cls.lists.get_parent_entry()
        cls.cf_entry = cls.custom_fields.get_parent_entry()

    def should_be_able_get_lists_parent_entry(self):
        self.assertIsInstance(self.lists_entry, AWeberEntry)

    def should_get_account_as_lists_parent(self):
        self.assertEqual(self.lists_entry.type, 'account')

    def should_be_able_get_custom_fields_parent_entry(self):
        self.assertIsInstance(self.cf_entry, AWeberEntry)

    def should_get_list_as_custom_fields_parent(self):
        self.assertEqual(self.cf_entry.type, 'list')


class TestParentEntryMethodForAccounts(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.AWeberAPI.adapter.requests = []
        cls.url = '/accounts/1/lists/303449/any_collection'
        cls.accounts = cls.AWeberAPI.load_from_url('/accounts')
        cls.accounts._get_size_from_url = Mock()
        cls.accounts._get_size_from_url.return_value = None, 1
        cls.accounts._get_request_endpoint_from_url = Mock()
        cls.accounts._get_request_endpoint_from_url.return_value = '/accounts'

    @classmethod
    def execute(cls):
        cls.entry = cls.accounts.get_parent_entry()

    def test_accounts_parent_should_be_none(self):
        self.assertEqual(self.entry, None)
