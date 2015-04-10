# Contents of this file are intended for the new format of ISO jobs starting
# from 6.1

import copy

from flask import current_app as app

from crawler import jenkins
from crawler import util


def extract_urls(text):
        iso, torrent = None, None
        if text:
            urls = util.find_urls(text)
            iso = util.try_index(urls, 0)
            torrent = util.try_index(urls, 1)

        return iso, torrent


def extract_downstream_builds_info(data):
    downstream = {}
    for build in data:
        job = build['jobName']
        result = build['result']
        build_number = build['buildNumber']

        downstream[job] = {
            'number': build_number,
            'result': result
        }

    return downstream


def query_test_all_job(job):
    jenkins_url = app.config['PRODUCT_JENKINS']
    rng = jenkins.get_job_build_range(jenkins_url, job)

    builds = {}
    for i in rng:
        try:
            raw = jenkins.get_build(jenkins_url, job, i, short=False)
        except Exception:
            continue

        upstream = jenkins.extract_parent_build_info(raw['actions'])

        # orphan build without upstream build. skip it
        if not upstream:
            continue

        upstream_build_number = upstream['upstreamBuild']
        downstream = extract_downstream_builds_info(raw['subBuilds'])

        build = {
            'result': raw['result'],
            'downstream': downstream
        }

        builds[upstream_build_number] = build

    return builds


def process_raw_build(raw):
    number = raw['number']
    result = raw['result']
    iso, torrent = extract_urls(raw['description'])

    values = {
        'result': result,
        'date': util.try_read_timestamp(raw['timestamp']/1000),
        'iso': iso,
        'torrent': torrent
    }

    return number, values


def query_main_job(job):
    jenkins_url = app.config['PRODUCT_JENKINS']
    rng = jenkins.get_job_build_range(jenkins_url, job)

    builds = {}
    for n in rng:
        try:
            raw = jenkins.get_build(jenkins_url, job, n, short=True)
        except Exception:
            continue

        number, processed_values = process_raw_build(raw)
        builds[number] = processed_values

    return builds


def get_iso_info(iso):
    _all = query_main_job('{0}.all'.format(iso))
    _test_all = query_test_all_job('{0}.test_all'.format(iso))

    builds = copy.deepcopy(_all)
    for n in _all.keys():
        if n in _test_all.keys():
            # note: this overrides 'status' of build
            # status of 'test_all' is more important than status of 'all'
            builds[n].update(_test_all[n])
        else:
            builds[n]['downstream'] = {}

    return builds
