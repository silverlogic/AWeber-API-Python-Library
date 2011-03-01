import re
from unittest import TestCase
from urllib import urlencode

from aweber_api import AWeberAPI, AWeberCollection, AWeberEntry
from mock_adapter import MockAdapter


class TestAWeberEntry(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        self.list = self.aweber.load_from_url('/accounts/1/lists/303449')

    def test_should_be_an_entry(self):
        self.assertEqual(type(self.list), AWeberEntry)
        self.assertEqual(self.list.type, 'list')

    def test_should_have_id(self):
        self.assertEqual(self.list.id, 303449)

    def test_should_have_other_properties(self):
        self.assertEqual(self.list.name, 'default303449')

    def test_should_have_child_collections(self):
        campaigns = self.list.campaigns
        self.assertEqual(type(campaigns), AWeberCollection)

class TestAWeberAccountEntry(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        self.account = self.aweber.load_from_url('/accounts/1')

    def test_should_be_an_entry(self):
        self.assertEqual(type(self.account), AWeberEntry)
        self.assertEqual(self.account.type, 'account')

    def test_should_be_able_get_web_forms(self):
        forms = self.account.get_web_forms()

class TestAccountGetWebForms(TestAWeberAccountEntry):

    def setUp(self):
        TestAWeberAccountEntry.setUp(self)
        self.forms = self.account.get_web_forms()

    def test_should_be_a_list(self):
        self.assertEqual(type(self.forms), list)

    def test_should_have_23_web_forms(self):
        self.assertEqual(len(self.forms), 23)

    def test_each_should_be_entry(self):
        for entry in self.forms:
            self.assertEqual(type(entry), AWeberEntry)
            self.assertEqual(entry.type, 'web_form')

    def test_each_should_have_correct_url(self):
        url_regex = '/accounts\/1\/lists\/\d*/web_forms/\d*'
        for entry in self.forms:
            self.assertTrue(re.match(url_regex, entry.url))

class TestSubscriber(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        sub_url = '/accounts/1/lists/303449/subscribers/1'
        self.subscriber = self.aweber.load_from_url(sub_url)

class TestGetAndSetData(TestSubscriber):

    def test_get_name(self):
        self.assertEqual(self.subscriber.name, 'Joe Jones')

    def test_set_name(self):
        self.subscriber.name = 'Randy Rhodes'
        self.assertEqual(self.subscriber.name, 'Randy Rhodes')

    def test_get_custom_fields(self):
        fields = self.subscriber.custom_fields
        self.assertEqual(fields['Make'], 'Honda')

    def test_set_custom_fields(self):
        self.subscriber.custom_fields['Make'] = 'Jeep'
        self.assertEqual(self.subscriber._data['custom_fields']['Make'], 'Jeep')
        fields = self.subscriber.custom_fields
        self.assertEqual(fields['Make'], 'Jeep')


class TestMovingSubscribers(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        subscriber_url = '/accounts/1/lists/303449/subscribers/1'
        new_list_url = '/accounts/1/lists/505454'
        self.subscriber = self.aweber.load_from_url(subscriber_url)
        self.subscriber._diff['name'] = 'Joe Schmoe'
        self.list = self.aweber.load_from_url(new_list_url)

        self.aweber.adapter.requests = []
        self.resp = self.subscriber.move(self.list)
        self.move_req = self.aweber.adapter.requests[0]
        self.get_req = self.aweber.adapter.requests[1]

    def test_returned_true(self):
        self.assertTrue(self.resp)

    def test_should_have_requested_move_with_post(self):
        self.assertEqual(self.move_req['method'], 'POST')

    def test_should_have_requested_move_on_subscriber(self):
        self.assertEqual(self.move_req['url'] , self.subscriber.url)

    def test_should_have_requested_move_with_correct_parameters(self):
        expected_params = {'ws.op': 'move', 'list_link': self.list.self_link}
        self.assertEqual(self.move_req['data'], expected_params)

    def test_should_make_two_requests(self):
        self.assertEqual(len(self.aweber.adapter.requests), 2)

    def test_should_refresh_subscriber_resource(self):
        self.assertEqual(self.get_req['method'], 'GET')
        self.assertEqual(self.get_req['url'] ,
            '/accounts/1/lists/505454/subscribers/3')

    def test_should_reset_diff(self):
        self.assertEqual(self.subscriber._diff, {})


class TestSavingSubscriberData(TestSubscriber):

    def setUp(self):
        TestSubscriber.setUp(self)
        self.aweber.adapter.requests = []
        self.subscriber.name = 'Gary Oldman'
        self.subscriber.custom_fields['Make'] = 'Jeep'
        self.resp = self.subscriber.save()
        self.req = self.aweber.adapter.requests[0]

    def test_returned_true(self):
        self.assertTrue(self.resp)

    def test_should_make_request(self):
        self.assertEqual(len(self.aweber.adapter.requests), 1)

    def test_should_have_requested_resource_url(self):
        self.assertEqual(self.req['url'] , self.subscriber.url)

    def test_should_have_requested_with_patch(self):
        self.assertEqual(self.req['method'], 'PATCH')

    def test_should_have_supplied_data(self):
        self.assertEqual(self.req['data']['name'], 'Gary Oldman')

    def test_should_not_include_unchanged_data(self):
        self.assertFalse('email' in self.req['data'])

    def test_should_given_all_custom_fields(self):
        # Make changed, Model did not
        self.assertEqual(self.req['data']['custom_fields']['Make'], 'Jeep')
        self.assertEqual(self.req['data']['custom_fields']['Model'], 'Civic')

class TestSavingInvalidSubscriberData(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        sub_url = '/accounts/1/lists/303449/subscribers/2'
        self.subscriber = self.aweber.load_from_url(sub_url)
        self.subscriber.name = 'Gary Oldman'
        self.subscriber.custom_fields['New Custom Field'] = 'Cookies'
        self.resp = self.subscriber.save()
        self.req = self.aweber.adapter.requests[0]

    def test_save_failed(self):
        self.assertFalse(self.resp)

class TestDeletingSubscriberData(TestSubscriber):

    def setUp(self):
        TestSubscriber.setUp(self)
        self.aweber.adapter.requests = []
        self.response = self.subscriber.delete()
        self.req = self.aweber.adapter.requests[0]

    def test_should_be_deleted(self):
        self.assertTrue(self.response)

    def test_should_have_made_request(self):
        self.assertEqual(len(self.aweber.adapter.requests), 1)

    def test_should_have_made_delete(self):
        self.assertEqual(self.req['method'], 'DELETE')

class TestFailedSubscriberDelete(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        sub_url = '/accounts/1/lists/303449/subscribers/2'
        self.subscriber = self.aweber.load_from_url(sub_url)
        self.aweber.adapter.requests = []
        self.response = self.subscriber.delete()
        self.req = self.aweber.adapter.requests[0]

    def test_should_have_failed(self):
        self.assertFalse(self.response)
