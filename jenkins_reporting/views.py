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


def _get_iso_test_types(builds):
    latest_build = next(build for build in builds if
                        (build.downstream.keys()
                         and build.result in ["SUCCESS", "FAILURE"]))
    return sorted(latest_build.downstream.keys())


def _get_ci_config(param_type, param):
    master_ci = app.config["MASTER_CI"]
    stable_ci = app.config["STABLE_CI"]

    if param in master_ci[param_type]:
        return master_ci
    elif param in stable_ci[param_type]:
        return stable_ci
    else:
        raise Exception("Invalid parameters {0}, {1}".format(
            param_type, param))


def _get_jobs_list(param_type):
    master_ci = app.config["MASTER_CI"]
    stable_ci = app.config["STABLE_CI"]

    return sorted(master_ci[param_type] + stable_ci[param_type],
                  reverse=True)


@iso_bp.route('/<version>')
def iso(version):
    job = "{0}.all".format(version)
    builds = db.get_iso_builds(job)
    if builds:
        test_types = _get_iso_test_types(builds)
    else:
        test_types = []
    ci = _get_ci_config("ISO_JOBS", version)

    return flask.render_template(
        "iso.html",
        builds=builds,
        test_types=test_types,
        version=version,
        jenkins=ci["JENKINS"],
        staging_jobs=_get_jobs_list("STAGING_JOBS"),
        iso_jobs=_get_jobs_list("ISO_JOBS"))


def _prepare_data_for_charts(top_n):
    data = []
    for k, v in top_n.items():
        data.append({"label": k, "value": v})

    return json.dumps(data)


@staging_bp.route('/<job>')
def staging(job):
    ci = _get_ci_config("STAGING_JOBS", job)

    builds = db.get_staging_builds(job)
    failed_builds = filter(lambda x: x['result'] == 'FAILURE', builds)

    metrics = stats.get_basic_stats(builds, failed_builds)
    top_by_team = _prepare_data_for_charts(
        stats.get_top_by_team(failed_builds))

    return flask.render_template(
        "staging.html",
        job=job,
        metrics=metrics,
        builds=failed_builds,
        jenkins=ci["JENKINS"],
        staging_jobs=_get_jobs_list("STAGING_JOBS"),
        iso_jobs=_get_jobs_list("ISO_JOBS"),
        top_by_team=top_by_team)
