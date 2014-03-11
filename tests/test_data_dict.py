from unittest2 import TestCase

from mock import Mock

from aweber_api.data_dict import DataDict


class TestDataDict(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.obj = Mock()
        cls.configure()
        cls.execute()

    @classmethod
    def configure(cls):
        cls.obj.data = {}
        cls.data = {
            'favorite food': 'Tacos',
            'favorite drink': 'Beer'
        }

    @classmethod
    def execute(cls):
        cls.dict = DataDict(cls.data, 'data', cls.obj)

    def test_exists(self):
        self.assertTrue(self.dict)

    def test_get_data(self):
        self.assertEqual(self.dict['favorite drink'], 'Beer')

    def test_set_data(self):
        self.dict['favorite food'] = 'Pizza'
        self.assertEqual(self.obj.data['favorite food'], 'Pizza')
