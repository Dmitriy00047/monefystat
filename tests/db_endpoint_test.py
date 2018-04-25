import unittest
from monefystat_api.app import app


class Create_db_test(unittest.TestCase):
    def test_create_returns_200(self):
        request, response = app.test_client.get('/create_db')
        assert response.status == 200

    def test_create_put_not_allowed(self):
        request, response = app.test_client.put('/create_db')
        assert response.status == 405


class Data_db_test(unittest.TestCase):
    def test_data_returns_200(self):
        request, response = app.test_client.get('/data')
        assert response.status == 200

    def test_data_put_not_allowed(self):
        request, response = app.test_client.put('/data')
        assert response.status == 405


class Drop_db_test(unittest.TestCase):
    def test_drop_returns_200(self):
        request, response = app.test_client.get('/drop_db')
        assert response.status == 200

    def test_drop_put_not_allowed(self):
        request, response = app.test_client.put('/drop_db')
        assert response.status == 405


if __name__ == "__main__":
    unittest.main()
