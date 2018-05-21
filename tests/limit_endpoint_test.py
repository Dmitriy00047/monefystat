import unittest
import json
from monefystat_api.app import app


def setup_module():
    request, response = app.test_client.get('/create_db')


def teardown_module():
    request, response = app.test_client.get('/drop_db')


class EUpsertLimitTest(unittest.TestCase):
    def test_post_limit_valid(self):
        body = {
            'category_name': 'taxi',
            'limit': '34',
            'start_date': '01-01-2012',
            'period': '34',
            'is_repeated': 'false'
        }
        request, response = app.test_client.post('/limit', data=json.dumps(body))
        assert response.status == 200

    def test_put_limit_invalid(self):
        body = {
            'category_name': 'taxi',
            'limit': '-34',
            'start_date': '01-01-2012',
            'period': '34',
            'is_repeated': 'false'
        }
        request, response = app.test_client.put('/limit', data=json.dumps(body))
        assert response.status == 400


class FDeleteLimitTest(unittest.TestCase):
    def test_delete_limit_exists(self):
        data = {'category_name': 'taxi'}
        request, response = app.test_client.delete('/limit', data=json.dumps(data))
        assert response.status == 200

    def test_delete_limit_not_exists(self):
        data = {'category_name': 'car'}
        request, response = app.test_client.delete('/limit', data=json.dumps(data))
        assert response.status == 404


class GGetLimitTest(unittest.TestCase):
    def test_get_concrete_limit(self):
        params = {'category_name': 'taxi'}
        request, response = app.test_client.get('/limit', params=params)
        assert response.status == 200

    def test_get_all_limits(self):
        request, response = app.test_client.get('/limit')
        assert response.status == 200

    def test_get_not_existig_limits(self):
        params = {'category_name': 'tax'}
        request, response = app.test_client.get('/limit', params=params)
        assert response.status == 404


if __name__ == '__main__':
    unittest.main()
