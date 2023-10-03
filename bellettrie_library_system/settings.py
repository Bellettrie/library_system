# flake8: noqa
from bellettrie_library_system.base_settings import *
import os

import environ

env = environ.Env()
environ.Env.read_env()
WSGI_APPLICATION = 'bellettrie_library_system.wsgi.application'

ALLOWED_HOSTS = ["*"]

LIBRARY_NAME = env("LIBRARY_NAME", default="Bellettrie")
LIBRARY_IMAGE_URL = env("LIBRARY_IMAGE_URL", default="images/wurm.png")
LIBRARY_DESCRIPTION = env("LIBRARY_DESCRIPTION",default="Bellettrie is a student run library at the University of Twente, specialised in Science Fiction and Fantasy")

SECRET_KEY = env("SECRET_KEY", default='9_meq=rl3q!wh4=lr4g9t)ra9l*o_d7!exbh&^brhj=*_xm5y*')
CROSS_LOGIN_KEY = env("CROSS_LOGIN_KEY", default='XP6kvnD5NQN3lL0zyjPeQumogu8y3YRtPi3NqKid9BA=')
CROSS_LOGIN_SECRET = env("CROSS_LOGIN_SECRET", default="VmYq3t6v")
CROSS_LOGIN_TIMEOUT = env("CROSS_LOGIN_TIMEOUT", default=3600 * 2)


DEBUG = env("DEBUG", default=True)
UPSIDE_DOWN = env("UPSIDE_DOWN", default=True)
CORS_ORIGIN_WHITELIST = env("CORS_ORIGIN_WHITELIST", default=['https://static.bellettrie.utwente.nl'])
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DB_ENG = env("DB_ENGINE", default="sqlite")
DB = None
if DB_ENG == "sqlite":
    DB = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, env("DB_SQLITE_FILE", default='db.sqlite3')),
    }
if DB_ENG == "mysql":
    DB = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env("DB_MYSQL_NAME"),
        'USER': env("DB_MYSQL_USER"),
        'PASSWORD': env("DB_MYSQL_PASSWORD"),
        'HOST': env("DB_MYSQL_HOST"),
        'PORT': env("DB_MYSQL_PORT"),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
if DB_ENG == "postgres":
    print("Postgres")
    
    DB = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("DB_POSTGRESQL_NAME"),
        'USER': env("DB_POSTGRESQL_USER"),
        'PASSWORD': env("DB_POSTGRESQL_PASSWORD"),
        'HOST': env("DB_POSTGRESQL_HOST"),
        'PORT': env("DB_POSTGRESQL_PORT"),
    }

DATABASES = {
    'default': DB
}

STATIC_URL = env("STATIC_URL", default='/root/')

# --------------------------------------------------
STATIC_ROOT = env("STATIC_ROOT",default=os.path.join(BASE_DIR, 'root'))
# -----------------------------------------------------
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'bootstrap'),
]

OLD_DB = "bellettrie"
OLD_USN = 'root'
OLD_PWD = 'root'

BASE_URL = '/'
EMAIL_PORT = env("EMAIL_PORT", default=1025)
EMAIL_HOST = env("EMAIL_HOST", default='127.0.0.1')

EMAIL_BACKEND = env("EMAIL_BACKEND",default='django.core.mail.backends.console.EmailBackend')

CRON_CLASSES = [
    "mail.cron.SendSingleEmail",
    "mail.cron.CleanMailLog",
    "lendings.cron.LateMails",
    "reservations.cron.ReservationCancel"
]
HOST=env("HOSTE",default="-")
EXTERNAL_UPLOAD_ENABLED = env("EXTERNAL_UPLOAD_ENABLED", default=False)
EXTERNAL_UPLOAD_URL_UPLOAD = env("EXTERNAL_UPLOAD_URL_UPLOAD", default='https://upload.bellettrie.net/upload')
EXTERNAL_UPLOAD_URL_DELETE = env("EXTERNAL_UPLOAD_URL_DELETE", default='https://upload.bellettrie.net/delete')
EXTERNAL_UPLOAD_URL_API_KEY = env("EXTERNAL_UPLOAD_URL_API_KEY", default='key')
EXTERNAL_UPLOAD_URL_DOWNLOAD_PREFIX = env("EXTERNAL_UPLOAD_URL_DOWNLOAD_PREFIX", default='https://bellettrie.net/static/uploads/')

IS_OPEN_URL = env("IS_OPEN_URL", default="https://dragoncounter.bellettrie.utwente.nl/crowds/api/")
