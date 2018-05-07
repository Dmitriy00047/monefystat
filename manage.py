from multiprocessing import Process
from telegram_bot.bot_handlers import bot
from monefystat_api import app
from config import web

if __name__ == '__main__':
    p = Process(target=bot.polling, kwargs={'none_stop': True})
    p.start()
    p.join()
    app.app.run(host=web['host'], port=web['port'])
