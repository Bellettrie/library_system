# flake8: noqa
import logging

from bellettrie_library_system.base_settings import *
import os

import environ

env = environ.Env()
environ.Env.read_env()
WSGI_APPLICATION = 'bellettrie_library_system.wsgi.application'

ALLOWED_HOSTS = ["*"]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LIBRARY_NAME = env("LIBRARY_NAME", default="Bellettrie")
LIBRARY_IMAGE_URL = env("LIBRARY_IMAGE_URL", default="images/wurm.png")
LIBRARY_DESCRIPTION = env("LIBRARY_DESCRIPTION",
                          default="Bellettrie is a student run library at the University of Twente, specialised in Science Fiction and Fantasy")

SECRET_KEY = env("SECRET_KEY", default='9_meq=rl3q!wh4=lr4g9t)ra9l*o_d7!exbh&^brhj=*_xm5y*')
CROSS_LOGIN_KEY = env("CROSS_LOGIN_KEY", default='XP6kvnD5NQN3lL0zyjPeQumogu8y3YRtPi3NqKid9BA=')
CROSS_LOGIN_SECRET = env("CROSS_LOGIN_SECRET", default="VmYq3t6v")
CROSS_LOGIN_TIMEOUT = env("CROSS_LOGIN_TIMEOUT", default=3600 * 2)

DEBUG = env("DEBUG", default=True)
UPSIDE_DOWN = env("UPSIDE_DOWN", default=True)
CORS_ORIGIN_WHITELIST = env("CORS_ORIGIN_WHITELIST", default=['https://static.bellettrie.utwente.nl'])
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


logging.info("Starting using postgresql database: %s", env("DB_POSTGRESQL_HOST"))

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
STATIC_ROOT = env("STATIC_ROOT", default=os.path.join(BASE_DIR, 'root'))
# -----------------------------------------------------
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'bootstrap'),
]

OLD_DB = "bellettrie"
OLD_USN = 'root'
OLD_PWD = 'root'

BASE_URL = env("BASE_URL", default="")
EMAIL_PORT = env("EMAIL_PORT", default=1025)
EMAIL_HOST = env("EMAIL_HOST", default='127.0.0.1')
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default='127.0.0.1')
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default='127.0.0.1')
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)
OVERRIDE_MAIL_ADDRESS = env("OVERRIDE_MAIL_ADDRESS", default=None)
EMAIL_BACKEND = env("EMAIL_BACKEND", default='django.core.mail.backends.console.EmailBackend')

CRON_CLASSES = [
    "mail.cron.SendSingleEmail",
    "mail.cron.CleanMailLog",
    "lendings.cron.LateMails",
    "reservations.cron.ReservationCancel"
]

HOST = env("MY_HOST_NAME", default="-")

IS_OPEN_URL = env("IS_OPEN_URL", default="https://dragoncounter.bellettrie.utwente.nl/crowds/api/")

MEDIA_ROOT = "/media/"
OVERRIDE_MAIL_ADDRESS = env("OVERRIDE_MAIL_ADDRESS", default='')
