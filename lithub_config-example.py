LITHUB_ROOT = "/home/path/to/your/project/root/directory"

# There are various ways to test/use email. Instructions at
# https://docs.djangoproject.com/en/1.3/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/home/path/to/store/emails/for/debug/'

# To be used by django-registration for registration
ACCOUNT_ACTIVATION_DAYS = 7
DEFAULT_FROM_EMAIL="test <test@example.com>"
