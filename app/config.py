import os


class Config(object):

    # Enable Flask's debugging features. Should be False in production
    DEBUG = os.environ.get('DEBUG') or True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-just-for-csrf-attacks-nbd'
