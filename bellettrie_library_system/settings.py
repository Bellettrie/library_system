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

OLD_DB = "oldsystem2"
OLD_USN = 'root'
OLD_PWD = 'root'
