from sanic import Sanic
from sanic.response import json, text
from sanic.request import RequestParameters
from config import dropbox, path
from transport.data_provider import DataProvider
from database import helpers
from processor import validator_data, mapper


app = Sanic()


@app.get("/smoke")
async def smoke_endpoint(request):
    return json({"hello": "world"})


# endpoint for Dropbox webhook initialization
@app.get("/webhook")
async def webhook_enable(request):
    args = RequestParameters()
    args = request.args
    return text(args["challenge"][0])


# endpoint for downloading file from dropbox
@app.post("/webhook")
async def webhook_reciver(request):
    obj = DataProvider(dropbox['token'], path)
    obj.get_newest_monefy_data()
    data = validator_data.validate_data(obj.download_path)
    if data:
        mapper.insert_transactions(data)
    return json({"message": "updated"}, status=200)


@app.get("/create_db")
async def create_endpoint(request):
    await helpers.create_db()
    return json(
        {"message": "DB created"},
        status=200
    )


@app.get("/drop_db")
async def drop_endpoint(request):
    await helpers.drop_db()
    return json(
        {"message": "DB droped"},
        status=200
    )


@app.get("/data")
async def data_endpoint(request):
    data = await helpers.get_all_data()
    return json(
        data,
        status=200
    )
