from datetime import date
from sanic.exceptions import abort
from sanic.response import json, text
from sanic.request import RequestParameters
from config import dropbox, path
from transport.data_provider import DataProvider
from database import helpers
from processor import validator_data, mapper


async def smoke_endpoint(request):
    return json({"hello": "world"})


# endpoint for Dropbox webhook initialization
async def webhook_enable(request):
    args = RequestParameters()
    args = request.args
    return text(args["challenge"][0])


# endpoint for downloading file from dropbox
async def webhook_reciver(request):
    obj = DataProvider(dropbox['token'], path)
    obj.get_newest_monefy_data()
    data = validator_data.validate_data(obj.download_path)
    if data:
        mapper.insert_transactions(data)
    return json({"message": "updated"}, status=200)


async def create_endpoint(request):
    await helpers.create_db()
    return json(
        {"message": "DB created"},
        status=200
    )


async def drop_endpoint(request):
    await helpers.drop_db()
    return json(
        {"message": "DB droped"},
        status=200
    )


async def data_endpoint(request):
    data = await helpers.get_all_data()
    return json(
        data,
        status=200
    )


async def set_limit(request):
    '''Inserts or updates limit in database'''
    additional_fields = ['category_name', 'limit', 'start_date', 'period', 'is_repeated']
    if set(request.json.keys()) == set(additional_fields):
        category_name = request.json.get('category_name')
        limit = int(request.json['limit'])
        start_date = 
        del request.json['category_name']
        try:
            
            await helpers.upsert_limit(category_name, **request.json)
            return text('Success', status=200)
        except Exception as e:
            return text('erorka')
    else:
        abort(400, 'Bad request')


async def get_limit():
    pass


async def clear_limit():
    pass
