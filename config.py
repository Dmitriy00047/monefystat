from os import environ as env
from os.path import dirname


path = dirname(__file__) + '/downloads/Monefy_data.csv'

web = {
    'host': env.get('WEB_HOST', 'localhost'),
    'port': int(env.get('WEB_PORT', '4000'))
}

db = {
    'user': env.get('DB_USER', 'user'),
    'password': env.get('DB_PASSWORD', 'password'),
    'host': env.get('DB_HOST', 'localhost'),
    'port': int(env.get('DB_PORT', 5432)),
    'dbname': env.get('DB_NAME', 'monefystat')
}

dropbox = {
    'token': env.get('DROPBOX_TOKEN', 'r_M1QDuIe2AAAAAAAAAALvqIS39RKjKZdjnZMO6S0mpZ8uwV3xlqkz-D20oAhrFO')
}

telegram = {
    'token': env.get('TELEGRAM_BOT_TOKEN', '551667714:AAH5lHg2Cic7kwW1VeAfPR14d4capoPxdHQ')
}
