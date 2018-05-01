from os import environ as env
from os.path import dirname


path = dirname(__file__) + '/downloads/Monefy_data.csv'

web = {
    'host': env.get('WEB_HOST', 'localhost'),
    'port': int(env.get('WEB_PORT', '3000'))
}

db = {
    'user': env.get('DB_USER', 'postgres'),
    'password': env.get('DB_PASSWORD', ''),
    'host': env.get('DB_HOST', 'localhost'),
    'port': int(env.get('DB_PORT', 5432)),
    'dbname': env.get('DB_NAME', 'monefystat')
}

dropbox = {
    'token': env.get('DROPBOX_TOKEN')
}
