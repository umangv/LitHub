# The root directory of your this Django application
# manage.py, settings.py, lithub_config.py, etc should be
# in this directory.
LITHUB_ROOT = "/home/path/to/your/project/root/directory"

# There are various ways to test/use email. Instructions at
# https://docs.djangoproject.com/en/1.3/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/home/path/to/store/emails/for/debug/'

# To be used by django-registration for registration
ACCOUNT_ACTIVATION_DAYS = 7
DEFAULT_FROM_EMAIL="test <test@example.com>"

# For FB integration
FB_APP_ID='12345'
FB_APP_SECRET='67890'
FB_REDIRECT_URL = "http://example.com"

# This allows facebook to become a valid authentication system
# Remove this if the fbconnect application is not being used
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'fbconnect.auth_backends.FBAuthentication',
)
