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
        await mapper.insert_transactions(data)
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


def _convert_limit_args(args):
    additional_fields = ['category_name', 'limit', 'start_date', 'period', 'is_repeated']
    if set(args.keys()) == set(additional_fields):
        category_name = args['category_name']
        del args['category_name']
        # tring to reinterpet in nessessary types
        try:
            args['limit'] = int(args['limit'])
            args['start_date'] = datetime.datetime.strptime(args['start_date'], '%d-%m-%Y').date()
            args['period'] = int(args['period'])
            args['is_repeated'] = args['is_repeated'].lower()

            if args['is_repeated'] == 'true' or args['is_repeated'] == 'false':
                args['is_repeated'] = (args['is_repeated'] == 'true')
            else:
                return None, None

            if args['limit'] <= 0 or args['period'] <= 0:
                return None, None

        except ValueError:
            return None, None

    return category_name, args


async def set_limit(request):
    '''Inserts or updates limit in database'''
    category_name, info = _convert_limit_args(request.json)
    if info:
        await helpers.upsert_limit(category_name, **info)
        return json({'message': 'limit setted'})
    else:
        return json({'message': 'bad request args'}, status=400)


async def get_limit(request):
    '''Selects category info from database'''
    data = await helpers.get_limit(request.args.get('category_name'))
    if data:
        return json(data)
    else:
        return json({'message': 'category doesnt exist'}, status=404)


async def clear_limit(request):
    '''Clears limit data in category'''
    category_name = request.json.get('category_name')
    if not category_name:
        return json({'message': 'category name is not specified'}, status=400)
    elif await helpers.get_limit(category_name):
        await helpers.delete_limit(category_name)
        return json({'message': 'category limit cleared'})
    else:
        return json({'message': 'category is not exists'}, status=404)


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
