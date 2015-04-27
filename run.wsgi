import sys
sys.path.insert(0, '/var/www/failorama')

from jenkins_reporting import application
from jenkins_reporting import config

def _create_app():
    conf = config.Production()
    return application.create_app(conf)


application = _create_app()
