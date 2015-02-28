from flask.ext import testing as flask_testing
from jenkins_reporting import application
from jenkins_reporting import config


class TestCase(flask_testing.TestCase):

    def create_app(self):
        return application.create_app(config.Testing())
