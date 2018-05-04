import json
import unittest
from monefystat_api.app import app


class ACreateTest(unittest.TestCase):
    def test_create_returns_200(self):
        request, response = app.test_client.get('/create_db')
        assert response.status == 200

    def test_create_put_not_allowed(self):
        request, response = app.test_client.put('/create_db')
        assert response.status == 405


class BDataTest(unittest.TestCase):
    def test_data_returns_200(self):
        request, response = app.test_client.get('/data')
        assert response.status == 200

    def test_data_put_not_allowed(self):
        request, response = app.test_client.put('/data')
        assert response.status == 405


class CDefinedPeriodTest(unittest.TestCase):
    def test_get_data_for_def_period_returns_200(self):
        params = {'category': 'еда', 'period': '7'}
        request, response = app.test_client.get(
            '/data_def_period', params=params)
        assert response.status == 200

    def test_get_data_for_def_period_put_not_allowed(self):
        request, response = app.test_client.put('/data_def_period')
        assert response.status == 405

    def test_get_data_for_def_period_query_in_get(self):
        params = {'category': 'еда', 'period': '7'}
        request, response = app.test_client.get(
            '/data_def_period', params=params)
        assert request.args.get(
            'category') == 'еда' and request.args.get('period') == '7'


class DCustomPeriodTest(unittest.TestCase):
    def test_get_data_for_custom_period_returns_200(self):
        params = {
            'category': 'еда',
            'start_date': '25-03-2018',
            'end_date': '25-04-2018'
        }
        request, response = app.test_client.get(
            '/data_custom_period', params=params)
        assert response.status == 200

    def test_get_data_for_custom_period_put_not_allowed(self):
        request, response = app.test_client.put('/data_custom_period')
        assert response.status == 405

    def test_get_data_for_custom_period_query_in_get(self):
        params = {
            'category': 'еда',
            'start_date': '25-03-2018',
            'end_date': '25-04-2018'
        }
        request, response = app.test_client.get('/data_custom_period', params=params)
        assert request.args.get('category') == 'еда' and \
            request.args.get('start_date') == '25-03-2018' and \
            request.args.get('end_date') == '25-04-2018'


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


class JDropTest(unittest.TestCase):
    def test_drop_returns_200(self):
        request, response = app.test_client.get('/drop_db')
        assert response.status == 200

    def test_drop_put_not_allowed(self):
        request, response = app.test_client.put('/drop_db')
        assert response.status == 405


if __name__ == '__main__':
    unittest.main()
