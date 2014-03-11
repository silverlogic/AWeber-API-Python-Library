from urllib import urlencode

from mock import Mock, patch, sentinel
import unittest2

from aweber_api.collection import AWeberCollection
from aweber_api.entry import AWeberEntry


class _basetest(unittest2.TestCase):

    @classmethod
    @patch('aweber_api.AWeberCollection.__init__', return_value=None)
    def setUpClass(cls, collection):
        cls.AWeberCollection = AWeberCollection(
            'http://www.example.com', sentinel.data, sentinel.adaptor)
        cls.configure()
        cls.execute()

    @classmethod
    def configure(cls):
        pass

    @classmethod
    def execute(cls):
        pass


class _basetestwithentry(unittest2.TestCase):

    @classmethod
    @patch('aweber_api.AWeberEntry')
    @patch('aweber_api.AWeberCollection.__init__', return_value=None)
    def setUpClass(cls, collection, entry):
        cls.AWeberCollection = AWeberCollection(
            'http://www.example.com', sentinel.data, sentinel.adaptor)
        cls.configure()
        cls.execute()

    @classmethod
    def configure(cls):
        pass

    @classmethod
    def execute(cls):
        pass


class DescribeMethodGetByID(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberCollection.load_from_url = Mock()
        cls.AWeberCollection.url = 'http://www.example.com'
        cls.AWeberCollection._data = []

    @classmethod
    def execute(cls):
        cls.output = cls.AWeberCollection.get_by_id(sentinel.id)

    def should_call_load_from_url(self):
        self.AWeberCollection.load_from_url.assert_called_once_with(
            "{0}/{1}".format(self.AWeberCollection.url, sentinel.id))


class DescribeMethodLoadPageForOffset(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberCollection.adapter = Mock()
        cls.AWeberCollection.url = 'http://www.example.com'
        cls.AWeberCollection._data = []
        cls.AWeberCollection._get_page_params = Mock()
        cls.AWeberCollection._get_page_params.return_value = ''
        cls.AWeberCollection._key_entries = Mock()
        cls.AWeberCollection._key_entries.return_value = ''

    @classmethod
    def execute(cls):
        cls.output = cls.AWeberCollection._load_page_for_offset(
            sentinel.offset)

    def should_call_get_page_params(self):
        self.AWeberCollection._get_page_params.assert_called_once_with(
            sentinel.offset)

    def should_make_get_request_with_correct_parameters(self):
        self.AWeberCollection.adapter.request.assert_called_once_with(
            'GET', self.AWeberCollection.url, '')


class DescribeMethodGetPageParams(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberCollection._data = Mock()
        cls.AWeberCollection._data.get.return_value = (
            '/accounts/1/lists?ws.start=10&ws.size=20')
        cls.offset = 40

    @classmethod
    def execute(cls):
        try:
            cls.returned = cls.AWeberCollection._get_page_params(cls.offset)
        except Exception as exception:
            cls.exception = exception

    def should_return_correct_page_size(self):
        self.assertEqual(self.returned['ws.size'], 20)

    def should_return_correct_page_offset(self):
        self.assertEqual(self.returned['ws.start'], 40)


class WhenGetPageParamsProcessesNextCollectionLinkIsNone(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberCollection._data = Mock()
        cls.AWeberCollection._data.get.return_value = None
        cls.offset = 10

    @classmethod
    def execute(cls):
        try:
            cls.returned = cls.AWeberCollection._get_page_params(cls.offset)
        except Exception as exception:
            cls.exception = exception

    def should_raise_stopiteration_when_next_collection_link_is_none(self):
        self.assertIsInstance(self.exception, StopIteration)


class DescribeMethodCreate(_basetestwithentry):

    @classmethod
    def configure(cls):
        cls.AWeberCollection.url = Mock(return_value=sentinel.url)

        cls.AWeberCollection._data = Mock()
        cls.AWeberCollection._data.return_value = [{'name': 'joe'}]

        cls.AWeberCollection.adapter = Mock()
        cls.AWeberCollection.adapter.request.return_value = {
            'location': sentinel.location}

    @classmethod
    def execute(cls):
        cls.output = cls.AWeberCollection.create()

    def should_make_post_request_with_correct_parameters(self):
        self.AWeberCollection.adapter.request.assert_any_call(
            'POST',
            self.AWeberCollection.url,
            {'ws.op': 'create'},
            response='headers',
        )

    def should_make_get_request_with_correct_parameters(self):
        self.AWeberCollection.adapter.request.assert_any_call(
            'GET', sentinel.location)

    def should_return_entry_type(self):
        self.assertIsInstance(self.output, AWeberEntry)


class DescribeMethodGetParentEntry(_basetestwithentry):

    @classmethod
    def configure(cls):
        cls.AWeberCollection.url = Mock(return_value='/accounts/1/lists')

        cls.AWeberCollection._data = Mock()
        cls.AWeberCollection._data.return_value = [{'name': 'joe'}]

        cls.AWeberCollection._partition_url = Mock()
        cls.AWeberCollection._partition_url.return_value = [
            'accounts',
            '1',
            'lists',
        ]

        cls.AWeberCollection._construct_parent_url = Mock()
        cls.AWeberCollection._construct_parent_url.return_value = (
            '/accounts/1/lists')

        cls.AWeberCollection.adapter = Mock()
        cls.AWeberCollection.adapter.request.return_value = {
            'location': sentinel.location}

    @classmethod
    def execute(cls):
        cls.output = cls.AWeberCollection.get_parent_entry()

    def should_make_get_request_with_correct_parameters(self):
        self.AWeberCollection.adapter.request.assert_called_once_with(
            'GET', self.AWeberCollection.url.return_value)

    def should_return_entry_type(self):
        self.assertIsInstance(self.output, AWeberEntry)


class DescribeMethodNextError(_basetest):

    @classmethod
    def configure(cls):
        cls.AWeberCollection._current = 20
        cls.AWeberCollection.total_size = 10

    @classmethod
    def execute(cls):
        try:
            cls.output = cls.AWeberCollection.next()
        except Exception as exception:
            cls.exception = exception

    def should_raise_stopiteration(self):
        self.assertIsInstance(self.exception, StopIteration)
