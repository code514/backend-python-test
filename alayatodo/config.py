import os


class EnvironConfig(object):
    DATABASE = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    TODOS_PER_PAGE = os.environ.get('TODOS_PER_PAGE', 3)
