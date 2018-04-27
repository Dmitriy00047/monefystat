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


class Defined_period_test(unittest.TestCase):
    def test_get_data_for_def_period_returns_200(self):
        params = {"category_name": "еда", "period": "7"}
        request, response = app.test_client.get("/data_def_period", params=params)
        assert response.status == 200

    def test_get_data_for_def_period_put_not_allowed(self):
        request, response = app.test_client.put("/data_def_period")
        assert response.status == 405

    def test_get_data_for_def_period_query_in_get(self):
        params = {"category_name": "еда", "period": "7"}
        request, response = app.test_client.get("/data_def_period", params=params)
        assert request.args.get("category_name") == "еда" and request.args.get("period") == "7"


class Custom_period_test(unittest.TestCase):
    def test_get_data_for_custom_period_returns_200(self):
        params = {"category_name": "еда", "start_date": "2018-03-25", "end_date": "2018-04-25"}
        request, response = app.test_client.get("/data_custom_period", params=params)
        assert response.status == 200

    def test_get_data_for_custom_period_put_not_allowed(self):
        request, response = app.test_client.put("/data_custom_period")
        assert response.status == 405

    def test_get_data_for_custom_period_query_in_get(self):
        params = {"category_name": "еда", "start_date": "2018-03-25", "end_date": "2018-04-25"}
        request, response = app.test_client.get("/data_custom_period", params=params)
        assert request.args.get("category_name") == "еда" and \
            request.args.get("start_date") == "2018-03-25" and \
            request.args.get("end_date") == "2018-04-25"


class Drop_db_test(unittest.TestCase):
    def test_drop_returns_200(self):
        request, response = app.test_client.get('/drop_db')
        assert response.status == 200

    def test_drop_put_not_allowed(self):
        request, response = app.test_client.put('/drop_db')
        assert response.status == 405


if __name__ == "__main__":
    unittest.main()
