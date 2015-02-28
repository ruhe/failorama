class Config(object):
    DEBUG = True
    TESTING = False

    _SQLALCHEMY_DATABASE_DATABASE = 'jenkins_reporting'
    _SQLALCHEMY_DATABASE_HOSTNAME = 'localhost'
    _SQLALCHEMY_DATABASE_PASSWORD = 'reporting'
    _SQLALCHEMY_DATABASE_USERNAME = 'reporting'

    # !!! Don't forget to override DB URI
    # in /etc/failorama/failorama.conf !!!
    SQLALCHEMY_DATABASE_URI = 'mysql://{u}:{p}@{h}/{d}'.format(
        d=_SQLALCHEMY_DATABASE_DATABASE,
        h=_SQLALCHEMY_DATABASE_HOSTNAME,
        p=_SQLALCHEMY_DATABASE_PASSWORD,
        u=_SQLALCHEMY_DATABASE_USERNAME
    )

    ###################################################
    # Override these in /etc/failorama/failorama.conf #
    ###################################################

    # Jenkins URL
    PRODUCT_JENKINS = ''

    # example: ['1.0', '1.1']
    ISO_VERSIONS = []

    # example: ['some_cache_job']
    IGNORED_ISO_JOBS = []

    # example ['1.1.test_staging_mirror', '1.0.test_staging_mirror']
    STAGING_JOBS = []


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_database.sqlite'


class Production(Config):
    DEBUG = False
