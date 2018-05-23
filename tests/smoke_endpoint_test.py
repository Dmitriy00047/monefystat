import unittest
from monefystat_api.app import app


class Smoke_test(unittest.TestCase):
    def test_smoke_returns_200(self):
        request, response = app.test_client.get('/smoke')
        assert response.status == 200

    def test_smoke_put_not_allowed(self):
        request, response = app.test_client.put('/smoke')
        assert response.status == 405


if __name__ == '__main__':
    unittest.main()
