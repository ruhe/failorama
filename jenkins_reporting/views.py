import flask
from flask import current_app as app

from jenkins_reporting import db

root_bp = flask.Blueprint('root', __name__)
iso_bp = flask.Blueprint('iso', __name__, template_folder='templates')
staging_bp = flask.Blueprint('staging', __name__, template_folder='templates')


@root_bp.route('/')
def index():
    default_version = app.config['ISO_VERSIONS'][0]
    url = flask.url_for('iso.iso', version=default_version)
    return flask.redirect(url)


@iso_bp.route('/<version>')
def iso(version):
    job = "{0}.all".format(version)
    builds = db.get_iso_builds(job)
    # Assuming all builds in 'version' have the same set of downstream jobs
    test_types = sorted(builds[0].downstream.keys())

    return flask.render_template("iso.html",
                                 builds=builds,
                                 test_types=test_types,
                                 version=version,
                                 jenkins=app.config['PRODUCT_JENKINS'],
                                 jobs=app.config['STAGING_JOBS'],
                                 versions=app.config['ISO_VERSIONS'])


@staging_bp.route('/<job>')
def staging(job):
    return flask.render_template("staging.html",
                                 job=job,
                                 builds=db.get_staging_builds(job),
                                 jenkins=app.config['PRODUCT_JENKINS'],
                                 jobs=app.config['STAGING_JOBS'],
                                 versions=app.config['ISO_VERSIONS'])
