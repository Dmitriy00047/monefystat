from ..monefystat_api.app import app
import unittest
import json


class Webhook_test(unittest.TestCase):
    def test_webhook_returns_200(self):
        params = {'challenge': 'abc112233'}
        request, response = app.test_client.get('/webhook', params=params)
        assert response.status == 200

    def test_webhook_put_not_allowed(self):
        request, response = app.test_client.put('/webhook')
        assert response.status == 405

    def test_webhook_response_get_with_data(self):
        params = {'challenge': 'abc112233'}
        request, response = app.test_client.get('/webhook', params=params)
        assert request.args.get('challenge') == 'abc112233'

    def test_webhook_post(self):
        data = {'key1': 'value1'}
        data = json.dumps(data)
        request, response = app.test_client.post('/webhook', data=data)
        assert request.json.get('key1') == 'value1'


if __name__ == "__main__":
    unittest.main()
