"""
Django settings for dgpf1 project.

Generated by 'django-admin startproject' using Django 4.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

##### ACCESS-CI CUSTOMIZATIONS #####
import json
import os
import sys
from dgpf1.fields import title, general_info, detail_result_display_fields
#import pdb
#pdb.set_trace()

if 'APP_CONFIG' not in os.environ:
  print('Missing APP_CONFIG environment variable')
  sys.exit(1)
try:
  with open(os.environ['APP_CONFIG'], 'r') as file:
    conf=file.read()
  CONF = json.loads(conf)
except (ValueError, IOError) as e:
  print('Failed to load APP_CONFIG={}'.format(os.environ['APP_CONFIG']))
  raise
#####


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONF['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONF['DEBUG']

ALLOWED_HOSTS = CONF['ALLOWED_HOSTS']


# Application definition

INSTALLED_APPS = [
    'provider',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
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

ROOT_URLCONF = 'dgpf1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'libraries': {
                'settings_value': 'templatetags.get_settings',
            },
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dgpf1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'USER': CONF['DJANGO_USER'],
    #     'PASSWORD': CONF['DJANGO_PASS'],
    #     'HOST': os.environ.get('PGHOST', CONF.get('DB_HOSTNAME_WRITE', 'localhost')),
    # }
  'default': {
      'ENGINE': 'django.db.backends.sqlite3',
      'NAME': BASE_DIR / 'db.sqlite3',
  }
}

for db in DATABASES:
    DATABASES[db]['NAME'] = CONF['DB_DATABASE']
    DATABASES[db]['ENGINE'] = 'django.db.backends.postgresql'
    DATABASES[db]['PORT'] = os.environ.get('PGPORT', CONF.get('DB_PORT', '5432'))
    DATABASES[db]['CONN_MAX_AGE'] = 600 # Persist DB connections
    DATABASES[db]['OPTIONS'] = {'options': '-c search_path=ed_dgpf1,public'}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'stream': {'level': 'DEBUG', 'class': 'logging.StreamHandler'},
        'null': {'level': 'DEBUG', 'class': 'logging.NullHandler'},
    },
    'loggers': {
        'django': {'handlers': ['stream'], 'level': 'INFO'},
        'django.db.backends': {'handlers': ['stream'], 'level': 'WARNING'},
        'globus_portal_framework': {'handlers': ['stream'], 'level': 'INFO'},
        'dgpf1': {'handlers': ['stream'], 'level': 'INFO', 'propagate': True},
    },
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = CONF['STATIC_ROOT']
STATICFILES_DIRS = [BASE_DIR / 'staticfiles']

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

################################################
### DGPF Customizations

# Your portal credentials for a Globus Auth Flow
SOCIAL_AUTH_GLOBUS_KEY = CONF['SOCIAL_AUTH_GLOBUS_KEY']
SOCIAL_AUTH_GLOBUS_SECRET = CONF['SOCIAL_AUTH_GLOBUS_SECRET']

# This is a general Django setting if views need to redirect to login
# https://docs.djangoproject.com/en/3.2/ref/settings/#login-url
LOGIN_URL = '/login/globus'

# This dictates which scopes will be requested on each user login
SOCIAL_AUTH_GLOBUS_SCOPE = [
    'urn:globus:auth:scope:search.api.globus.org:search',
]

INSTALLED_APPS.extend(['globus_portal_framework', 'social_django'])

MIDDLEWARE.extend(['globus_portal_framework.middleware.ExpiredTokenMiddleware',
    'globus_portal_framework.middleware.GlobusAuthExceptionMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware'])

# Authentication backends setup OAuth2 handling and where user data should be
# stored
AUTHENTICATION_BACKENDS = [
    'globus_portal_framework.auth.GlobusOpenIdConnect',
    'django.contrib.auth.backends.ModelBackend',
]

for t in TEMPLATES:
    if t['BACKEND'] != 'django.template.backends.django.DjangoTemplates':
        continue
    t['OPTIONS']['context_processors'].append('globus_portal_framework.context_processors.globals')

SEARCH_INDEXES = {
    'hpc-ed-v1': {
        'name': 'HPC Training Material (HPC-ED) - Alpha catalog v1',
        'uuid': '0e8be9d5-99d7-4641-ae43-f72b40bb8a5c',
        'facets': [
            {'name': 'Expertise Level', 'field_name': 'Expertise_Level' },
            {'name': 'Outcomes', 'field_name': 'Learning_Outcome' },
            {'name': 'Target Group', 'field_name': 'Target_Group' },
            {'name': 'Learning Resource Type', 'field_name': 'Learning_Resource_Type'},
            {'name': 'Learning Outcome', 'field_name': 'Learning_Outome' },
            {'name': 'Rating', 'field_name': 'Rating', 'type': 'numeric_histogram', 'size': 5, 'histogram_range': {'low': 0.0, 'high': 5.0}},
            {'name': 'Duration', 'field_name': 'Duration', 'type': 'numeric_histogram', 'size': 8, 'histogram_range': {'low': 30, 'high': 480}},
            {'name': 'Keywords', 'field_name': 'Keywords' },
            {'name': 'License', 'field_name': 'License' },
            {'name': 'URL Type', 'field_name': 'Resource_URL_Type' },
            {'name': 'Provider ID', 'field_name': 'Provider_ID' },
        ],
        'facet_modifiers': [
            'globus_portal_framework.modifiers.facets.drop_empty',
            'dgpf1.facet_modifiers.lookup_replace_provider_id',
        ],
        'fields': [
            ('title', title),
            ('general_info', general_info),
            ('detail_result_display_fields', detail_result_display_fields),
        ],
    },
    'hpc-ed-pearc24': {
        'name': 'HPC Training Material (HPC-ED) - PEARC24 tutorial catalog',
        'uuid': 'a2017194-aa8a-41d2-af21-ba8ea79039e5',
        'facets': [
            {'name': 'Expertise Level', 'field_name': 'Expertise_Level' },
            {'name': 'Outcomes', 'field_name': 'Learning_Outcome' },
            {'name': 'Target Group', 'field_name': 'Target_Group' },
            {'name': 'Learning Resource Type', 'field_name': 'Learning_Resource_Type'},
            {'name': 'Learning Outcome', 'field_name': 'Learning_Outome' },
            {'name': 'Rating', 'field_name': 'Rating', 'type': 'numeric_histogram', 'size': 5, 'histogram_range': {'low': 0.0, 'high': 5.0}},
            {'name': 'Duration', 'field_name': 'Duration', 'type': 'numeric_histogram', 'size': 8, 'histogram_range': {'low': 30, 'high': 480}},
            {'name': 'Keywords', 'field_name': 'Keywords' },
            {'name': 'License', 'field_name': 'License' },
            {'name': 'URL Type', 'field_name': 'Resource_URL_Type' },
            {'name': 'Provider ID', 'field_name': 'Provider_ID' },
        ],
        'facet_modifiers': [
            'globus_portal_framework.modifiers.facets.drop_empty',
            'dgpf1.facet_modifiers.lookup_replace_provider_id',
        ],
        'fields': [
            ('title', title),
            ('general_info', general_info),
            ('detail_result_display_fields', detail_result_display_fields),
        ],
    },
    'hpc-ed-v1-match-all': {
        'name': 'HPC Training Material (HPC-ED) - Alpha catalog v1 (match all)',
        'uuid': '0e8be9d5-99d7-4641-ae43-f72b40bb8a5c',
        'filter_match': 'match-all',
        'facets': [
            {'name': 'Expertise Level', 'field_name': 'Expertise_Level' },
            {'name': 'Outcomes', 'field_name': 'Learning_Outcome' },
            {'name': 'Target Group', 'field_name': 'Target_Group' },
            {'name': 'Learning Resource Type', 'field_name': 'Learning_Resource_Type'},
            {'name': 'Learning Outcome', 'field_name': 'Learning_Outome' },
            {'name': 'Rating', 'field_name': 'Rating', 'type': 'numeric_histogram', 'size': 5, 'histogram_range': {'low': 0.0, 'high': 5.0}},
            {'name': 'Duration', 'field_name': 'Duration', 'type': 'numeric_histogram', 'size': 8, 'histogram_range': {'low': 30, 'high': 480}},
            {'name': 'Keywords', 'field_name': 'Keywords' },
            {'name': 'License', 'field_name': 'License' },
            {'name': 'URL Type', 'field_name': 'Resource_URL_Type' },
            {'name': 'Provider ID', 'field_name': 'Provider_ID' },
        ],
        'facet_modifiers': [
            'globus_portal_framework.modifiers.facets.drop_empty',
            'dgpf1.facet_modifiers.lookup_replace_provider_id',
        ],
        'fields': [
            ('title', title),
            ('general_info', general_info),
            ('detail_result_display_fields', detail_result_display_fields),
        ],
    },
}

PROJECT_TITLE = 'Search Pilot'
APP_VERSION = CONF.get('APP_VERSION', '')
