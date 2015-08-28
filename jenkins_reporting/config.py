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

    MASTER_CI = {
        "JENKINS": "",
        "STAGING_JOBS": [],
        "ISO_JOBS": []
    }

    STABLE_CI = {
        "JENKINS": "",
        "STAGING_JOBS": [],
        "ISO_JOBS": []
    }

    IGNORED_ISO_JOBS = []


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_database.sqlite'


class Production(Config):
    DEBUG = False
