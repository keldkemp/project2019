import dj_database_url

from .settings import *  # noqa

DEBUG = True

ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    'crmproject2019designer.herokuapp.com',
]

# django-multitenant db engine for foreign keys is broken, use default
DATABASES['default'] = dj_database_url.config(
    conn_max_age=600, ssl_require=True)
