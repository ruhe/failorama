import datetime
import re

from crawler import util

JOB_INFO_URL = \
    "{0}/job/{1}/api/json?tree=firstBuild[number],lastBuild[number]"

BUILD_SHORT_INFO_URL = \
    "{0}/job/{1}/{2}/api/json?tree=result,timestamp,number,description"

BUILD_INFO_URL = \
    "{0}/job/{1}/{2}/api/json?tree=" \
    "actions[causes[upstreamBuild,upstreamProject]]," \
    "subBuilds[buildNumber,jobName,result]," \
    "number,result,timestamp"


def get_job_build_range(jenkins, job):
    url = JOB_INFO_URL.format(jenkins, job)
    resp = util.get_json(url)

    first = resp['firstBuild']['number']
    last = resp['lastBuild']['number']

    return xrange(last, first, -1)


def get_build(jenkins, job, number, short=True):
    if short:
        url_template = BUILD_SHORT_INFO_URL
    else:
        url_template = BUILD_INFO_URL

    url = url_template.format(jenkins, job, number)
    resp = util.get_json(url)
    return resp


def extract_parent_build_info(actions):
    # Jenkins API returns a structure of the following form:
    # {
    #     "actions": [
    #         {},    # <-- *Note this empty element*
    #         {
    #             "causes": [
    #                 {
    #                     "upstreamBuild": 276,
    #                     "upstreamProject": "6.1.all"
    #                 }
    #             ]
    #         },
    #     ]
    # }
    #
    # Thus we have to filter out all the empty elements and return only one
    # of them which contains upstream build number and project name.

    filtered = [x for x in actions
                if x
                and 'causes' in x.keys()
                and x['causes']
                and x['causes'][0]
                and 'upstreamBuild' in x['causes'][0].keys()
                and 'upstreamProject' in x['causes'][0].keys()]

    try:
        return filtered[0]['causes'][0]
    except IndexError:
        return None


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
