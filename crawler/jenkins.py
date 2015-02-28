import datetime
import re

from crawler import util

JOB_INFO_URL = \
    "{0}/job/{1}/api/json?tree=firstBuild[number],lastFailedBuild[number]"
BUILD_INFO_URL = \
    "{0}/job/{1}/{2}/api/json?tree=result,timestamp,number,description"


def get_job_build_range(jenkins, job):
    url = JOB_INFO_URL.format(jenkins, job)
    resp = util.get_json(url)

    first = resp['firstBuild']['number']
    last = resp['lastFailedBuild']['number']

    return xrange(last, first, -1)


def get_build(jenkins, job, number):
    url = BUILD_INFO_URL.format(jenkins, job, number)
    resp = util.get_json(url)
    return resp


def find_bugs(build):
    descr = build['description']
    if not descr:
        return []

    urls = util.find_urls(descr)
    bugs = [re.findall(r"\d{7}", x) for x in urls]
    if not bugs:
        return bugs

    bugs = sum(bugs, [])
    bugs = map(int, bugs)
    bugs = list(set(bugs))

    return bugs


def _failed_build(build):
    return build['result'] == 'FAILURE'


def _timestamp2str(ts):
    # round timestamp to seconds
    dt = datetime.datetime.fromtimestamp(ts/1000)
    return dt.strftime('%Y-%m-%d')


def get_failed_builds(jenkins, job):
    rng = get_job_build_range(jenkins, job)

    failed_builds = []
    for i in rng:
        build = get_build(jenkins, job, i)
        if _failed_build(build):
            build['bugs'] = find_bugs(build)
            build['date'] = _timestamp2str(build['timestamp'])
            util.remove_key(build, 'description')
            failed_builds.append(build)

        print('.'),
    print

    return failed_builds
