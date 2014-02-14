from unittest import TestCase

from dingus import Dingus

from aweber_api.data_dict import DataDict


class TestDataDict(TestCase):

    def setUp(self):
        self.obj = Dingus()
        self.obj.data = {}
        self.data = {
            'favorite food': 'Tacos',
            'favorite drink': 'Beer'
        }
        self.dict = DataDict(self.data, 'data', self.obj)

    def test_exists(self):
        self.assertTrue(self.dict)

    def test_get_data(self):
        self.assertEqual(self.dict['favorite drink'], 'Beer')

    def test_set_data(self):
        self.dict['favorite food'] = 'Pizza'
        self.assertEqual(self.obj.data['favorite food'], 'Pizza')
