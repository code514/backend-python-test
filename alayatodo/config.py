import os


class EnvironConfig(object):
    DATABASE = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
