import logging

from flask import current_app as app

from crawler import jenkins
from crawler import util

log = logging.getLogger(__name__)


def should_insert_newer_build(builds, build, upstream_number):
    """Returns true if should update mapping from downstream
    build to matching upstream build.

    Each upstream build might have several downstream builds.
    We need to select only the latest one.
    """
    if util.has_key(builds, upstream_number):
        other = builds[upstream_number]
        if other["timestamp"] > build["timestamp"]:
            return False

    return True


def get_build_info(jenkins_url, job, build_number):
    raw = jenkins.get_build(jenkins_url, job, build_number, short=False)
    upstream = jenkins.extract_parent_build_info(raw['actions'])

    record = {
        'timestamp': raw['timestamp'],
        'number': raw['number'],
        'result': raw['result'],
    }

    return upstream, record


def get_builds(jenkins_url, job, days_back=2):
    log.info("Getting builds for <{0}>".format(job))

    rng = jenkins.get_job_build_range(jenkins_url, job)
    stopline = util.days_ago_timestamp(7)

    builds = {}
    for i in rng:
        try:
            upstream_build, build = get_build_info(jenkins_url, job, i)
        except Exception:
            continue

        # orphan build without upstream build. skip it
        if not upstream_build:
            continue

        timestamp = build['timestamp'] / 1000

        if timestamp < stopline:
            stopline_str = util.timestamp2str(timestamp)
            log.info("Stop line {0} for job {1}".format(stopline_str, job))
            break

        upstream_number = upstream_build["upstreamBuild"]

        if should_insert_newer_build(builds, build, upstream_number):
            builds[upstream_number] = build

    return builds


def extract_urls(text):
    iso, torrent = None, None
    if text:
        urls = util.find_urls(text)
        iso = util.try_index(urls, 0)
        torrent = util.try_index(urls, 1)

    return iso, torrent


def process_raw_build(raw):
    number = raw['number']
    result = raw['result']
    iso, torrent = extract_urls(raw['description'])

    values = {
        'result': result,
        'date': util.try_read_timestamp(raw['timestamp'] / 1000),
        'iso': iso,
        'torrent': torrent,
        'downstream': {}
    }

    return number, values


def query_main_job(jenkins_url, job):
    log.info("Getting main job {0}".format(job))
    rng = jenkins.get_job_build_range(jenkins_url, job)
    stopline = util.days_ago_timestamp(7)

    builds = {}
    for n in rng:
        try:
            raw = jenkins.get_build(jenkins_url, job, n, short=True)
        except Exception:
            continue

        timestamp = raw["timestamp"] / 1000
        if timestamp < stopline:
            stopline_str = util.timestamp2str(timestamp)
            log.info("Stop line {0} for job {1}".format(stopline_str, job))
            break

        number, processed_values = process_raw_build(raw)
        builds[number] = processed_values

    return builds


def collect_test_results(jenkins_url, job):
    ignore_list = app.config['IGNORED_ISO_JOBS']
    downstream_jobs = jenkins.get_downstream_build_names(jenkins_url,
                                                         job,
                                                         ignore_list)

    test_results = {}
    for test_job in downstream_jobs:
        test_results[test_job] = get_builds(jenkins_url, test_job)

    return test_results


def match_test_results(upstream, downstream):
    for build in upstream.values():
        number = build['number']
        for test_job, test_results in downstream.items():
            if number in test_results.keys():
                if "downstream" not in build.keys():
                    build["downstream"] = {}
                build['downstream'][test_job] = test_results[number]


def get_test_all_results(jenkins_url, job):
    test_all_builds = get_builds(jenkins_url, job)
    test_results = collect_test_results(jenkins_url, job)
    match_test_results(test_all_builds, test_results)

    return test_all_builds


def get_iso_info(jenkins_url, iso):
    main_job_name = "{0}.all".format(iso)
    test_all_job_name = "{0}.test_all".format(iso)

    main_job_builds = query_main_job(jenkins_url, main_job_name)
    test_results = get_test_all_results(jenkins_url, test_all_job_name)

    for number, values in main_job_builds.items():
        if util.has_key(test_results, number):
            to_copy = test_results[number]
            values["result"] = to_copy["result"]
            if util.has_key(to_copy, "downstream"):
                values["downstream"] = to_copy["downstream"]

    return main_job_builds
