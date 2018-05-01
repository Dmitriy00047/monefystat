from sanic import Blueprint
from monefystat_api.service_resource import \
        smoke_endpoint, \
        webhook_enable, \
        webhook_reciver, \
        drop_endpoint, \
        create_endpoint, \
        data_endpoint, \
        get_data_for_custom_period_endpoint, \
        get_data_for_defined_period_endpoint, \
        set_limit


bp = Blueprint('api_v1')

bp.add_route(smoke_endpoint, '/smoke', methods=['GET'])
bp.add_route(webhook_enable, '/webhook', methods=['GET'])
bp.add_route(webhook_reciver, '/webhook', methods=['POST'])
bp.add_route(create_endpoint, '/create_db', methods=['GET'])
bp.add_route(drop_endpoint, '/drop_db', methods=['GET'])
bp.add_route(data_endpoint, '/data', methods=['GET'])
bp.add_route(get_data_for_defined_period_endpoint, '/data_def_period', methods=['GET'])
bp.add_route(get_data_for_custom_period_endpoint, '/data_custom_period', methods=['GET'])
bp.add_route(set_limit, '/limit', methods=['PUT', 'POST'])
