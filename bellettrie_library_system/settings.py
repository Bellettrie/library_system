# flake8: noqa
from bellettrie_library_system.base_settings import *
import os

WSGI_APPLICATION = 'bellettrie_library_system.wsgi.application'

SECRET_KEY = '9_meq=rl3q!wh4=lr4g9t)ra9l*o_d7!exbh&^brhj=*_xm5y*'

DEBUG = True
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_URL = '/root/'
# --------------------------------------------------
STATIC_ROOT = os.path.join(BASE_DIR, 'root')
# -----------------------------------------------------
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'bootstrap'),
]

OLD_DB = "bellettrie"
OLD_USN = 'root'
OLD_PWD = 'root'

BASE_URL = 'http://127.0.0.1:4000/'
EMAIL_PORT = 1025
EMAIL_HOST ='127.0.0.1'
FAKE_MAIL = True
FAKE_MAIL_ADDRESS = 'nander@nander.net'

CORS_ORIGIN_WHITELIST = [
    'https://nander.net:4000',
]