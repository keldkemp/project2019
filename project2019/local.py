from .settings import *  # noqa

DEBUG = True

ALLOWED_HOSTS = [
    'kagent.herokuapp.com',
    '127.0.0.1'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
