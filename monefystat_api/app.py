from sanic import Sanic
from .api_v1 import bp


app = Sanic()
app.blueprint(bp)
