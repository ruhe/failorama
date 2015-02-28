import flask
import flask.ext.sqlalchemy

from jenkins_reporting import views
from jenkins_reporting.extensions import db


def create_app(config_object_str):
    app = flask.Flask(__name__)
    app.config.from_object(config_object_str)
    app.config.from_pyfile('/etc/failorama/failorama.conf', silent=True)

    app.register_blueprint(views.root_bp, url_prefix='/')
    app.register_blueprint(views.iso_bp, url_prefix='/iso')
    app.register_blueprint(views.staging_bp, url_prefix='/staging')

    db.init_app(app)

    return app
