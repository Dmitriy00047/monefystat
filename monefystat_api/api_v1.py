from sanic import Blueprint
from monefystat_api.service_resource import drop_endpoint, data_endpoint
from monefystat_api.service_resource import smoke_endpoint, webhook_enable, webhook_reciver, create_endpoint


bp = Blueprint('api_v1')

bp.add_route(smoke_endpoint, "/smoke", methods=['GET'])

bp.add_route(webhook_enable, "/webhook", methods=['GET'])

bp.add_route(webhook_reciver, "/webhook", methods=['POST'])

bp.add_route(create_endpoint, "/create_db", methods=['GET'])

bp.add_route(drop_endpoint, "/drop_db", methods=['GET'])

bp.add_route(data_endpoint, "/data", methods=['GET'])
