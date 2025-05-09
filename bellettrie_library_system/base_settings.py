"""
Django settings for bellettrie_library_system project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.urls import reverse


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESERVATION_TIMEOUT_DAYS = 14

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mail_templated',
    'works',
    'members',
    'series',
    'lendings',
    'reservations',
    'config',
    'inventarisation',
    'recode',
    'book_code_generation',
    'creators',
    'mail',
    'public_pages',
    'datamining',
    'search',
    'tables',
    'tasks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bellettrie_library_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins':
                [
                    'bellettrie_library_system.templatetags.paginator_tag',
                    'tables.templatetags.render_square',
                    'tables.templatetags.member_lending_table',
                    'tables.templatetags.lending_table',
                    'tables.templatetags.publications_list_for_member',
                    'tables.templatetags.reservation_table',
                    'tables.templatetags.item_detail_table',
                    'tables.templatetags.lending_history_table',
                ],
            'context_processors':
                [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
        },
    },
]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

LOGOUT_REDIRECT_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/'


def GET_MENU():
    from config.menu import MenuItem

    my_menu = []
    my_menu.append(MenuItem('Home', reverse('homepage'), None, 'top-left', [], icon='fa fa-home'))
    my_menu.append(MenuItem('Our Collection', reverse('works.list'), None, 'top-left', [], icon='fa fa-book'))
    my_menu.append(MenuItem('Become a member', reverse('named_page', args=('basic', 'member',)), None, 'top-left', [], icon='fa fa-user'))
    my_menu.append(MenuItem('Board / Committees', reverse('named_page', args=('basic', 'committees',)), None, 'top-left', [], icon='fa fa-users'))
    my_menu.append(MenuItem('Konnichiwa', reverse('named_page', args=('konnichiwa', 'home',)), None, 'top-left', [], icon=''))

    # my_menu.append(MenuItem('Corona', reverse('named_page', args=('basic', 'corona',)), None, 'top-right', [], icon='fa fa-exclamation-circle'))
    my_menu.append(MenuItem('About', reverse('named_page', args=('basic', 'about',)), None, 'top-right', [], icon='fa fa-user'))
    my_menu.append(MenuItem('Contact', reverse('named_page', args=('basic', 'contact',)), None, 'top-right', [], icon='fa fa-info'))

    my_menu.append(MenuItem('Login', reverse('login'), None, 'top-right', [], anonymous=True, icon='fa fa-sign-in-alt'))
    my_menu.append(MenuItem('Logout', reverse('logout'), None, 'top-right', [], anonymous=False, icon='fa fa-sign-out-alt', is_logout=True))

    my_menu.append(MenuItem('Catalog', reverse('works.list'), None, 'sidebar', [], anonymous=False, icon='fa fa-book'))
    my_menu.append(MenuItem('Members', reverse('members.list'), 'members.view_member', 'sidebar', [], anonymous=None, icon='fa fa-user'))
    my_menu.append(MenuItem('Lendings', reverse('lendings.list'), 'lendings.view_lending', 'sidebar', [], anonymous=None, icon='fa fa-bookmark'))
    my_menu.append(MenuItem('Reservations', reverse('lendings.reserve.list'), 'reservations.view_reservation', 'sidebar', [], anonymous=None, icon='fa fa-bookmark'))
    holiday_item = MenuItem('Holidays', reverse('holiday.list'), 'config.view_holiday', 'sidebar', [], anonymous=None, icon='fa fa-plane')
    my_menu.append(MenuItem('Settings', reverse('logout'), None, 'sidebar', [holiday_item], only_subitems=True, icon='fa fa-cogs'))

    uploads = MenuItem('Uploads', reverse('list_uploads'), 'public_pages.change_publicpage', 'sidebar', [], anonymous=None, icon='fa fa-upload')
    web_management = MenuItem('List Web Pages', reverse('list_pages'), 'public_pages.view_publicpage', 'sidebar', [], anonymous=None, icon='fa fa-newspaper')
    my_menu.append(MenuItem('Web Management', reverse('logout'), None, 'sidebar', [web_management, uploads], only_subitems=True, icon='fa fa-globe'))

    new_work = MenuItem('New Work', reverse('works.publication.new'), 'works.add_publication', 'sidebar', [], anonymous=None, icon='fa fa-book')
    new_series = MenuItem('New Series', reverse('series.new'), 'series.add_series', 'sidebar', [], anonymous=None, icon='fa fa-book')
    new_creator = MenuItem('New Author', reverse('creator.new'), 'creators.add_creator', 'sidebar', [], anonymous=None, icon='fa fa-book')
    inventarisation = MenuItem('Inventarisations', reverse('inventarisation.list'), 'inventarisation.view_inventarisation', 'sidebar', [], anonymous=None, icon='fa fa-clipboard-list')
    recode_list = MenuItem('Recode list', reverse('recode.list'), 'recode.view_recode', 'sidebar', [], anonymous=None, icon='fa fa-clipboard-list')
    codes = MenuItem('Book Codes', reverse('book_code.code_list'), 'works.change_work', 'sidebar', [], anonymous=None, icon='fa fa-clipboard-list')

    my_menu.append(
        MenuItem('Catalog Management', reverse('logout'), None, 'sidebar', [new_work, new_series, new_creator, inventarisation, recode_list, codes], only_subitems=True, icon='fa fa-book'))
    anon_members = MenuItem('Anonymous users', reverse('members.list.anon'), 'members.change_member', 'sidebar', [], anonymous=None, icon='fa fa-clipboard-list')
    member_stats = MenuItem('Member Statistics', reverse('datamining.membership_stats'), 'members.change_member', 'sidebar', [], anonymous=None, icon='fa fa-clipboard-list')
    lending_stats = MenuItem('Lending Statistics', reverse('datamining.lending_stats'), 'works.view_work', 'sidebar', [], anonymous=None, icon='fa fa-clipboard-list')

    members_list = MenuItem('Member Filter', reverse('datamining.members'), 'members.change_member', 'sidebar', [], anonymous=None, icon='fa fa-clipboard-list')
    my_menu.append(MenuItem('Datamining', reverse('logout'), None, 'sidebar', [members_list, anon_members, member_stats, lending_stats], only_subitems=True, icon='fa fa-book'))
    my_menu.append(MenuItem('Docs', reverse('named_page', args=("docs", "home",)), None, 'sidebar', [], anonymous=False, icon='fa fa-book'))

    return my_menu


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
