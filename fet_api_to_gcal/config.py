import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    CLIENT_ID = "1008498480829-sqolhtujjmaelhot5pdrk82o5qj9hige.apps.googleusercontent.com"
    CLIENT_SECRET = "uzWWHqekA-0mFO3wBBPlJw6V"


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
