from multiprocessing import Process
from telegram_bot.bot_handlers import bot
from monefystat_api import app
from config import web

if __name__ == '__main__':
    p1 = Process(target=bot.polling, kwargs={'none_stop': True})
    p1.start()

    p2 = Process(target=app.app.run, kwargs={'host': web['host'], 'port': web['port']})
    p2.start()

    p1.join()
    p2.join()
