from pathlib import Path
from os import getenv as env

# Should environment variables be loaded using the dotenv module or not
USE_DOTENV = True

if USE_DOTENV:
    from dotenv import load_dotenv
    load_dotenv(Path('.') / '.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG', 'False').lower() in ('true', 'yes', '1')

ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')

# Main Site URL for email templates, etc.
SITE_URL = f'https://{ALLOWED_HOSTS[0]}/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blogs',
    'users',
    'django_ckeditor_5',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ief.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates/',],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.helpers.context_processors.notification_count',
                'common.context_processors.project_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'ief.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
    {
        'NAME': 'users.helpers.password_validation.BlankCharactersValidator',
    },

]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
    # "/var/www/static/",
]

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email sending
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = f'Igni et Ferro <{EMAIL_HOST_USER}>'

# Signing in and Signing up 
LOGIN_PAGE_NAME = 'login_page'

LOGIN_URL = '/login/'

LOGIN_RESTRICTION_TIMEOUT = 60 * 15

LOGIN_ATTEMPTS_MAX = 10

# Passwords
PASSWORD_RESET_RESTRICTION_TIMEOUT = 60 * 60

PASSWORD_RESET_ATTEMPTS_MAX = 5

# Registration (sending an application)
APPLICATION_RESTRICTION_TIMEOUT = 60 * 60

APPLICATION_ATTEMPTS_MAX = 5

APPLICATIONS_APPROVE_AUTOMATICALLY = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'standard': {
            'format': '[%(levelname)s]: %(message)s'
        },
        'verbose': {
            'format': '|%(asctime)s| [%(levelname)s in %(funcName)s by %(name)s logger]: %(message)s'
        }
    },
    
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': BASE_DIR / 'logs/error_log.log'
        },
        'user_approved_file': {
            'level': "INFO",
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': BASE_DIR / 'logs/user_approved_log.log'
        },
        'user_login_restrictions_file': {
            'level': "INFO",
            'class': "logging.FileHandler",
            'formatter': 'verbose',
            'filename': BASE_DIR / 'logs/user_restrictions_log.log'
        }
    },
    
    'loggers': {
        'users.helpers.users.approve_application': {
            'handlers': ['user_approved_file'],
            'level': "INFO",
            'propagate': False,
        },
        'users.views.login_page': {
            'handlers': ['user_login_restrictions_file', 'console'],
            'level': "INFO",
            'propagate': False
        }
    },
    
    'root': {
        'handlers': ['console', 'error_file'],
        'level': 'ERROR',
    }
        
}

# Cache, Redis, and Celery
REDIS_URL = env("REDIS_URL")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL", "REDIS_URL")

CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", "REDIS_URL")

# CKEditor settings 
CKEDITOR_5_MAX_FILE_SIZE = 10

CKEDITOR_5_FILE_STORAGE = "blogs.storage.BlogUploadsStorage"

CKEDITOR_5_FILE_UPLOAD_PERMISSION = "authenticated" 

customColorPalette = [
      {
          'color': 'hsl(4, 90%, 58%)',
          'label': 'Red'
      },
      {
          'color': 'hsl(340, 82%, 52%)',
          'label': 'Pink'
      },
      {
          'color': 'hsl(291, 64%, 42%)',
          'label': 'Purple'
      },
      {
          'color': 'hsl(262, 52%, 47%)',
          'label': 'Deep Purple'
      },
      {
          'color': 'hsl(231, 48%, 48%)',
          'label': 'Indigo'
      },
      {
          'color': 'hsl(207, 90%, 54%)',
          'label': 'Blue'
      },
  ]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}
