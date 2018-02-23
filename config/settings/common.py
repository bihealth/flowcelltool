# -*- coding: utf-8 -*-
"""
Django settings for Flowcell Tool project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import environ
import itertools

ROOT_DIR = environ.Path(__file__) - 3  # (flowcelltool/config/settings/common.py - 3 = flowcelltool/)
APPS_DIR = ROOT_DIR.path('flowcelltool')

env = environ.Env()

# .env file, should load only in development environment
READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)

if READ_DOT_ENV_FILE:
    # Operating System Environment variables have precedence over variables
    # defined in the .env file, that is to say variables from the .env files
    # will only be used if not defined as environment variables.
    env_file = str(ROOT_DIR.path('.env'))
    env.read_env(env_file)


# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    'django.contrib.humanize',

    # For Postgres full-text-search:
    'django.contrib.postgres',

    # Admin
    'django.contrib.admin',
)
THIRD_PARTY_APPS = (
    'crispy_forms',  # Form layouts
    'markdown_deux',  # Markdown support
    'rules.apps.AutodiscoverRulesConfig',  # django rules engine
    'db_file_storage',  # storing files in database
    'rest_framework',     # Django REST Framework (DRF)
    'generic_relations',  # generic relations for DRF
    'formtools',  # for form wizards
)

# Apps specific for this project go here.
LOCAL_APPS = (
    # custom users app
    'flowcelltool.users.apps.UsersConfig',
    # flowcell management
    'flowcelltool.flowcells',
    # messages with attachments
    'flowcelltool.threads',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'flowcelltool.contrib.sites.migrations'
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_SENDER = env('EMAIL_SENDER', default='noreply@example.com')
EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX', default='')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""Manuel Holtgrewe""", 'manuel.holtgrewe@bihealth.de'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///flowcelltool'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

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

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'flowcelltool.users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'flowcelltool.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'flowcell_list'
LOGIN_URL = 'login'

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'


# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

# Your common stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

# File storage configuration
# ------------------------------------------------------------------------------
DEFAULT_FILE_STORAGE = 'db_file_storage.storage.DatabaseFileStorage'

# FLYNN WORKAROUND
import pip

try:
    import rest_framework
except ImportError:
    print('Flynn issue #3932 workaround: installing rest_framework..')

    pip.main([
        'install',
        'git+git://github.com/tomchristie/django-rest-framework.git@master#egg=djangorestframework'])
# END FLYNN WORKAROUND

# LDAP configuration
# ------------------------------------------------------------------------------

# Enable LDAP if configured
if env.bool('ENABLE_LDAP', None) is True:
    # import ldap
    # from django_auth_ldap.config import LDAPSearch
    # FLYNN WORKAROUND
    import pip

    try:
        import ldap

    except ImportError:
        print('Flynn issue #3932 workaround: installing ldap..')

        pip.main([
            'install',
            'git+git://github.com/holtgrewe/pyldap.git@'
            'fce3b934e9b2d7d1a538fc37d7c4ed4cfe18fae1#egg=pyldap'])

        import ldap

    # from django_auth_ldap.config import LDAPSearch

    try:
        from django_auth_ldap.config import LDAPSearch

    except Exception:
        print('Flynn issue #3932 workaround: installing django-auth-ldap..')
        pip.main([
            'install',
            'django-auth-ldap==1.2.8'])

        from django_auth_ldap.config import LDAPSearch
    # FLYNN WORKAROUND ENDS

    # Default values
    LDAP_DEFAULT_CONN_OPTIONS = {
        ldap.OPT_REFERRALS: 0}
    LDAP_DEFAULT_FILTERSTR = '(sAMAccountName=%(user)s)'
    LDAP_DEFAULT_ATTR_MAP = {
        'first_name': 'givenName',
        'last_name': 'sn',
        'email': 'mail'}

    # Primary LDAP server
    AUTH_LDAP_SERVER_URI = env.str('AUTH_LDAP_SERVER_URI', None)
    AUTH_LDAP_BIND_DN = env.str('AUTH_LDAP_BIND_DN', None)
    AUTH_LDAP_BIND_PASSWORD = env.str('AUTH_LDAP_BIND_PASSWORD', None)
    AUTH_LDAP_CONNECTION_OPTIONS = LDAP_DEFAULT_CONN_OPTIONS

    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        env.str('AUTH_LDAP_USER_SEARCH_BASE', None),
        ldap.SCOPE_SUBTREE, LDAP_DEFAULT_FILTERSTR)
    AUTH_LDAP_USER_ATTR_MAP = LDAP_DEFAULT_ATTR_MAP
    AUTH_LDAP_USERNAME_DOMAIN = env.str('AUTH_LDAP_USERNAME_DOMAIN', None)

    AUTHENTICATION_BACKENDS = tuple(itertools.chain(
        ('flowcelltool.users.backends.PrimaryLDAPBackend',),
        AUTHENTICATION_BACKENDS,
    ))

    # Secondary LDAP server (optional)
    AUTH_LDAP2_USERNAME_SUFFIX = None

    if env.bool('ENABLE_LDAP_SECONDARY', None) is True:
        # Primary LDAP server
        AUTH_LDAP2_SERVER_URI = env.str('AUTH_LDAP2_SERVER_URI', None)
        AUTH_LDAP2_BIND_DN = env.str('AUTH_LDAP2_BIND_DN', None)
        AUTH_LDAP2_BIND_PASSWORD = env.str('AUTH_LDAP2_BIND_PASSWORD', None)
        AUTH_LDAP2_CONNECTION_OPTIONS = LDAP_DEFAULT_CONN_OPTIONS

        AUTH_LDAP2_USER_SEARCH = LDAPSearch(
            env.str('AUTH_LDAP2_USER_SEARCH_BASE', None),
            ldap.SCOPE_SUBTREE, LDAP_DEFAULT_FILTERSTR)
        AUTH_LDAP2_USER_ATTR_MAP = LDAP_DEFAULT_ATTR_MAP
        AUTH_LDAP2_USERNAME_DOMAIN = env.str('AUTH_LDAP2_USERNAME_DOMAIN')

        AUTHENTICATION_BACKENDS = tuple(itertools.chain(
            ('flowcelltool.users.backends.SecondaryLDAPBackend',),
            AUTHENTICATION_BACKENDS,
        ))

    if DEBUG:
        import logging, logging.handlers
        logfile = "django-ldap-debug.log"
        my_logger = logging.getLogger('django_auth_ldap')
        my_logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(
            logfile, maxBytes=1024 * 500, backupCount=5)
        my_logger.addHandler(handler)


# Django REST Framework Configuration
# ------------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # TODO: use rules engine
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

# Disable/Enable REST API
# ------------------------------------------------------------------------------

REST_API = env.bool('FLOWCELLTOOL_REST_API', False)

# Disable/Enable Sending of emails
# ------------------------------------------------------------------------------

FLOWCELLS_SEND_EMAILS = env.bool('FLOWCELLTOOL_SEND_EMAILS', False)
