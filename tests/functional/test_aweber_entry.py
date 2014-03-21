from re import match
from unittest2 import TestCase

from mock import patch, sentinel
from mock_adapter import MockAdapter

from aweber_api import AWeberAPI, AWeberCollection, AWeberEntry
from aweber_api.base import APIException


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


class TestAWeberEntry(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()

    @classmethod
    def execute(cls):
        cls.list = cls.AWeberAPI.load_from_url('/accounts/1/lists/303449')

    def should_return_item_as_an_entry(self):
        self.assertEqual(type(self.list), AWeberEntry)

    def should_return_item_as_correct_type(self):
        self.assertEqual(self.list.type, 'list')

    def should_return_item_with_correct_id(self):
        self.assertEqual(self.list.id, 303449)

    def should_have_other_properties(self):
        self.assertEqual(self.list.name, 'default303449')

    def should_have_child_collections(self):
        self.assertEqual(type(self.list.campaigns), AWeberCollection)


class TestAWeberAccount(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()

    @classmethod
    def execute(cls):
        cls.account = cls.AWeberAPI.load_from_url('/accounts/1')

    def should_be_an_entry(self):
        self.assertEqual(type(self.account), AWeberEntry)

    def should_return_account_type(self):
        self.assertEqual(self.account.type, 'account')


class TestAccountFindSubscribers(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.account = cls.AWeberAPI.load_from_url('/accounts/1')
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def execute(cls):
        cls.subscribers = cls.account.findSubscribers(email='joe@example.com')
        cls.request = cls.AWeberAPI.adapter.requests[0]

    def should_return_collection_of_subscribers(self):
        self.assertIsInstance(self.subscribers, AWeberCollection)

    def should_return_collection_with_correct_number_of_entries(self):
        self.assertEqual(len(self.subscribers), 1)

    def should_return_correct_self_link(self):
        self.assertEqual(
            self.subscribers[0].self_link, (
                'https://api.aweber.com/1.0/accounts/1/lists/303449/'
                'subscribers/1'
            ),
        )

    def should_handle_errors_from_findSubscribers(self):
        self.assertRaises(
            APIException, self.account.findSubscribers, name='bob')


class TestAccountGetWebForms(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.account = cls.AWeberAPI.load_from_url('/accounts/1')
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def execute(cls):
        cls.forms = cls.account.get_web_forms()

    def should_return_a_list_type(self):
        self.assertEqual(type(self.forms), list)

    def should_return_181_web_forms(self):
        self.assertEqual(len(self.forms), 181)

    def should_return_each_item_as_type_entry(self):
        for entry in self.forms:
            self.assertEqual(type(entry), AWeberEntry)

    def should_return_each_item_as_a_webform_type(self):
        for entry in self.forms:
            self.assertEqual(entry.type, 'web_form')

    def should_return_each_item_with_correct_url(self):
        url_regex = r'/accounts\/1\/lists\/\d*/web_forms/\d*'
        for entry in self.forms:
            self.assertTrue(match(url_regex, entry.url))


class TestGetAndSetData(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.sub_url = '/accounts/1/lists/303449/subscribers/1'

    @classmethod
    def execute(cls):
        cls.subscriber = cls.AWeberAPI.load_from_url(cls.sub_url)
        cls.AWeberAPI.adapter.requests = []

    def should_get_saved_name(self):
        self.assertEqual(self.subscriber.name, 'Joe Jones')

    def should_set_name(self):
        self.subscriber.name = 'Randy Rhodes'
        self.assertEqual(self.subscriber.name, 'Randy Rhodes')

    def should_get_custom_fields(self):
        fields = self.subscriber.custom_fields
        self.assertEqual(fields['Color'], 'blue')

    def should_set_custom_fields_in_data(self):
        self.subscriber.custom_fields['Color'] = 'Red'
        self.assertEqual(
            self.subscriber._data['custom_fields']['Color'], 'Red')

    def should_set_custom_fields(self):
        self.subscriber.custom_fields['Color'] = 'Red'
        fields = self.subscriber.custom_fields
        self.assertEqual(fields['Color'], 'Red')

    def should_be_able_get_activity(self):
        self.subscriber.get_activity()


class TestMovingSubscribers(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.subscriber_url = '/accounts/1/lists/303449/subscribers/1'
        cls.new_list_url = '/accounts/1/lists/505454'
        cls.subscriber = cls.AWeberAPI.load_from_url(cls.subscriber_url)
        cls.subscriber._diff['name'] = 'Joe Schmoe'
        cls.list = cls.AWeberAPI.load_from_url(cls.new_list_url)
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def move_subscriber(cls, **kwargs):
        cls.AWeberAPI.adapter.requests = []
        cls.resp = cls.subscriber.move(cls.list, **kwargs)
        cls.move_req = cls.AWeberAPI.adapter.requests[0]
        cls.get_req = cls.AWeberAPI.adapter.requests[1]

    @classmethod
    def execute(cls):
        cls.move_subscriber()

    def should_returned_true(self):
        self.assertTrue(self.resp)

    def should_have_requested_move_with_post(self):
        self.assertEqual(self.move_req['method'], 'POST')

    def should_have_requested_move_on_subscriber(self):
        self.assertEqual(self.move_req['url'], self.subscriber.url)

    def should_have_requested_move_with_correct_parameters(self):
        expected_params = {'ws.op': 'move', 'list_link': self.list.self_link}
        self.assertEqual(self.move_req['data'], expected_params)

    def should_make_two_requests(self):
        self.assertEqual(len(self.AWeberAPI.adapter.requests), 2)

    def should_make_get_method_request(self):
        self.assertEqual(self.get_req['method'], 'GET')

    def should_refresh_subscriber_resource(self):
        self.assertEqual(
            self.get_req['url'], '/accounts/1/lists/505454/subscribers/3')

    def should_reset_diff(self):
        self.assertEqual(self.subscriber._diff, {})

    def test_should_accept_last_followup_message_number_sent(self):
        self.move_subscriber(last_followup_message_number_sent=999)
        expected_params = {
            'ws.op': 'move',
            'list_link': self.list.self_link,
            'last_followup_message_number_sent': 999,
        }

        self.assertEqual(self.move_req['data'], expected_params)


class TestSavingSubscriberData(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.subscriber_url = '/accounts/1/lists/303449/subscribers/1'
        cls.subscriber = cls.AWeberAPI.load_from_url(cls.subscriber_url)
        cls.AWeberAPI.adapter.requests = []
        cls.subscriber.name = 'Gary Oldman'
        cls.subscriber.custom_fields['Color'] = 'Red'

    @classmethod
    def execute(cls):
        cls.resp = cls.subscriber.save()
        cls.req = cls.AWeberAPI.adapter.requests[0]

    def should_return_true(self):
        self.assertTrue(self.resp)

    def should_make_request(self):
        self.assertEqual(len(self.AWeberAPI.adapter.requests), 1)

    def should_have_requested_resource_url(self):
        self.assertEqual(self.req['url'], self.subscriber.url)

    def should_have_requested_with_patch(self):
        self.assertEqual(self.req['method'], 'PATCH')

    def should_have_supplied_data(self):
        self.assertEqual(self.req['data']['name'], 'Gary Oldman')

    def should_not_include_unchanged_data(self):
        self.assertFalse('email' in self.req['data'])

    def should_given_all_custom_fields(self):
        # Make changed, Model did not
        self.assertEqual(self.req['data']['custom_fields']['Color'], 'Red')
        self.assertEqual(self.req['data']['custom_fields']['Walruses'], '')


class TestSavingInvalidSubscriberData(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.subscriber_url = '/accounts/1/lists/303449/subscribers/2'
        cls.subscriber = cls.AWeberAPI.load_from_url(cls.subscriber_url)
        cls.AWeberAPI.adapter.requests = []
        cls.subscriber.name = 'Gary Oldman'
        cls.subscriber.custom_fields['New Custom Field'] = 'Cookies'

    @classmethod
    def execute(cls):
        try:
            cls.resp = cls.subscriber.save()
            cls.req = cls.AWeberAPI.adapter.requests[0]

        except (APIException) as exception:
            cls.exception = exception

    def should_raise_APIException(self):
        self.assertIsInstance(self.exception, APIException)


class TestDeletingSubscriberData(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.subscriber_url = '/accounts/1/lists/303449/subscribers/1'
        cls.subscriber = cls.AWeberAPI.load_from_url(cls.subscriber_url)
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def execute(cls):
        try:
            cls.response = cls.subscriber.delete()
            cls.req = cls.AWeberAPI.adapter.requests[0]

        except (APIException) as exception:
            cls.exception = exception

    def should_return_true_when_item_deleted(self):
        self.assertTrue(self.response)

    def should_have_made_request(self):
        self.assertEqual(len(self.AWeberAPI.adapter.requests), 1)

    def should_have_made_delete(self):
        self.assertEqual(self.req['method'], 'DELETE')


class TestFailedSubscriberDelete(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.sub_url = '/accounts/1/lists/303449/subscribers/2'
        cls.subscriber = cls.AWeberAPI.load_from_url(cls.sub_url)
        cls.AWeberAPI.adapter.requests = []

    @classmethod
    def execute(cls):
        try:
            cls.subscriber.delete()

        except (APIException) as exception:
            cls.exception = exception

    def should_raise_APIException(self):
        self.assertIsInstance(self.exception, APIException)


class TestGettingParentEntry(_BaseTest):

    @classmethod
    def configure(cls):
        cls.AWeberAPI.adapter = MockAdapter()
        cls.list = cls.AWeberAPI.load_from_url('/accounts/1/lists/303449')
        cls.list = cls.AWeberAPI.load_from_url('/accounts/1/lists/303449')
        cls.account = cls.AWeberAPI.load_from_url('/accounts/1')
        cls.custom_field = cls.AWeberAPI.load_from_url(
            '/accounts/1/lists/303449/custom_fields/1')

    @classmethod
    def execute(cls):
        cls.list_entry = cls.list.get_parent_entry()
        cls.cf_entry = cls.custom_field.get_parent_entry()
        cls.acct_entry = cls.account.get_parent_entry()

    def should_be_able_get_list_parent_entry(self):
        self.assertIsInstance(self.list_entry, AWeberEntry)

    def should_get_account_as_lists_parent(self):
        self.assertEqual(self.list_entry.type, 'account')

    def should_be_able_get_custom_field_parent_entry(self):
        self.assertIsInstance(self.cf_entry, AWeberEntry)

    def should_get_list_as_custom_fields_parent(self):
        self.assertEqual(self.cf_entry.type, 'list')

    def should_be_none_for_parent_for_account(self):
        self.assertEqual(self.acct_entry, None)
