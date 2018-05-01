import datetime
from sanic.exceptions import abort
from sanic.response import json, text
from sanic.request import RequestParameters
from config import dropbox, path
from transport.data_provider import DataProvider
from database import helpers
from processor import validator_data, mapper


async def smoke_endpoint(request):
    return json({'hello': 'world'})


# endpoint for Dropbox webhook initialization
async def webhook_enable(request):
    args = RequestParameters()
    args = request.args
    return text(args['challenge'][0])


# endpoint for downloading file from dropbox
async def webhook_reciver(request):
    obj = DataProvider(dropbox['token'], path)
    obj.get_newest_monefy_data()
    data = validator_data.validate_data(obj.download_path)
    if data:
        mapper.insert_transactions(data)
    return json({'message': 'updated'}, status=200)


async def create_endpoint(request):
    await helpers.create_db()
    return json({'message': 'DB created'})


async def drop_endpoint(request):
    await helpers.drop_db()
    return json({'message': 'DB droped'})


async def data_endpoint(request):
    data = await helpers.get_all_data()
    return json(data)


async def set_limit(request):
    '''Inserts or updates limit in database'''
    additional_fields = ['category_name', 'limit', 'start_date', 'period', 'is_repeated']
    if set(request.json.keys()) == set(additional_fields):
        category_name = request.json['category_name']
        limit = int(request.json['limit'])
        start_date = datetime.datetime.strptime(request.json['start_date'], "%d-%m-%Y").date()
        period = int(request.json['period'])
        if request.json['is_repeated'].lower() == 'true' or request.json['is_repeated'].lower() == 'false':
            isrepeated = request.json['is_repeated'].lower() == 'true'
        else:
            raise ValueError
        await helpers.upsert_limit(
            category_name, limit=limit, start_date=start_date, period=period, is_repeated=isrepeated)
        return text('Success', status=200)
    else:
        abort(400, 'Bad request')


async def get_limit():
    pass


async def clear_limit():
    pass


async def get_data_for_defined_period_endpoint(request):
    try:
        category = request.args['category'][0]
        period = request.args['period'][0]
    except KeyError:
        abort(400, message='Blank space in query')
    data = await helpers.get_data_period(category_name=category, period=period)
    return json(data)


async def get_data_for_custom_period_endpoint(request):
    try:
        category = request.args['category'][0]
        start_date = request.args['start_date'][0]
        end_date = request.args['end_date'][0]
    except KeyError:
        abort(400, message='Blank space in query')
    data = await helpers.get_data_period(category_name=category, start_date=start_date, end_date=end_date)
    return json(data)
