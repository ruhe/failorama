import json

import flask
from flask import current_app as app

from jenkins_reporting import db
from jenkins_reporting import stats

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

    # Find first build which has a list of downstream builds
    good_build = next(build for build in builds if (build.downstream.keys()))
    test_types = sorted(good_build.downstream.keys())

    return flask.render_template("iso.html",
                                 builds=builds,
                                 test_types=test_types,
                                 version=version,
                                 jenkins=app.config['PRODUCT_JENKINS'],
                                 jobs=app.config['STAGING_JOBS'],
                                 versions=app.config['ISO_VERSIONS'])


def _prepare_data_for_charts(top_n):
    data = []
    for k, v in top_n.items():
        data.append({"label": k, "value": v})

    return json.dumps(data)


@staging_bp.route('/<job>')
def staging(job):
    builds = db.get_staging_builds(job)
    top_by_target = _prepare_data_for_charts(stats.get_top_by_target(builds))
    top_by_team = _prepare_data_for_charts(stats.get_top_by_team(builds))

    return flask.render_template("staging.html",
                                 job=job,
                                 builds=builds,
                                 jenkins=app.config['PRODUCT_JENKINS'],
                                 jobs=app.config['STAGING_JOBS'],
                                 versions=app.config['ISO_VERSIONS'],
                                 top_by_target=top_by_target,
                                 top_by_team=top_by_team)
