from unittest import TestCase
from aweber_api import AWeberAPI, AWeberCollection, AWeberEntry
from mock_adapter import MockAdapter


class TestAWeberCollection(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        self.lists = self.aweber.load_from_url('/accounts/1/lists')
        self.aweber.adapter.requests = []

    def test_should_be_a_collection(self):
        self.assertTrue(type(self.lists), AWeberCollection)

    def test_should_have_24_lists(self):
        self.assertTrue(len(self.lists), 24)

    def test_should_be_able_get_each_via_offset(self):
        for i in range(0, 23):
            list = self.lists[i]
            self.assertEqual(type(list), AWeberEntry)
            self.assertEqual(list.type, 'list')

    def test_should_be_able_to_iterate_on_collection(self):
        list_number = 0
        for list in self.lists:
            self.assertEqual(type(list), AWeberEntry)
            self.assertEqual(list.type, 'list')
            list_number += 1
        self.assertEqual(list_number, 24)

    def test_should_support_get_by_id(self):
        list = self.lists.get_by_id(303449)
        self.assertEqual(type(list), AWeberEntry)
        self.assertEqual(list.type, 'list')
        self.assertEqual(list.id, 303449)

    def test_should_support_find_method(self):
        base_url = '/accounts/1/lists/303449/subscribers'
        subscriber_collection = self.aweber.load_from_url(base_url)
        self.aweber.adapter.requests = []
        subscribers = subscriber_collection.find(email='joe@example.com')
        request = self.aweber.adapter.requests[0]

        assert subscribers != False
        assert isinstance(subscribers, AWeberCollection)
        assert len(subscribers) == 1
        assert subscribers[0].self_link == \
                'https://api.aweber.com/1.0/accounts/1/lists/303449/subscribers/50205517'
        assert request['url'] == \
            '{0}?ws.op=find&email=joe%40example.com'.format(base_url)

    def test_find_should_handle_errors(self):
        base_url = '/accounts/1/lists/303449/subscribers'
        subscriber_collection = self.aweber.load_from_url(base_url)
        self.aweber.adapter.requests = []
        subscribers = subscriber_collection.find(name='joe')
        request = self.aweber.adapter.requests[0]

        assert subscribers == False
        assert request['url'] == \
            '{0}?ws.op=find&name=joe'.format(base_url)
