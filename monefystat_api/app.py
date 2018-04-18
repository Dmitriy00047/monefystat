from os.path import dirname, abspath
from sanic import Sanic
from sanic.response import json
from sanic.response import text
from sanic.request import RequestParameters

from ..keys import DROPBOX_TOKEN
from ..transport.data_provider import DataProvider
from service_resource import drop_db_endpoint, create_db_endpoint

PATH = dirname(dirname(abspath(__file__))) + '/downloads/Monefy_data.csv'
DIR = '/monefy'
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
    obj = DataProvider(DROPBOX_TOKEN, PATH)
    obj.get_newest_monefy_data()
    return json(
        {'message': ''},
        status=200
    )


@app.get("/create_db")
async def create_endpoint(request):
    create_db_endpoint()
    return json(
        {"message": "DB created"},
        status=200
    )


@app.get("/drop_db")
async def drop_endpoint(request):
    drop_db_endpoint()
    return json(
        {"message": "DB droped"},
        status=200
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
