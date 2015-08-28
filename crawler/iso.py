# Contents of this file are intended for the the old format of ISO jobs
# which existed before 6.1
# NOTE: this format is a subject of deprecation and should be eventually
# removed
import logging
import lxml.etree as et
from StringIO import StringIO

from flask import current_app
import requests

import crawler as current_path
from crawler import iso2
from crawler import util
from jenkins_reporting import db

log = logging.getLogger(__name__)

mapping = {
    'number': util.try_int,
    'result': util.ident,
    'upstreamProject': util.ident,
    'upstreamBuild': util.try_int,
    'description': util.ident,
    'timestamp': util.try_int
}


def build_dom(xml_path, xslt_path):
    # in some cases python lxml will fail to fetch xml from URL
    # thus we have to fetch xml first and then pass a stream to lxml to parse
    xml = StringIO(requests.get(xml_path).text)
    dom = et.parse(xml)
    xslt = et.parse(xslt_path)
    transform = et.XSLT(xslt)
    return transform(dom)


def get_dom(jenkins_url, job):
    link = "{0}/job/{1}/api/xml?depth=1".format(jenkins_url, job)

    xslt_path = util.file_abs_path('build.xslt', current_path.__file__)
    return build_dom(link, xslt_path)


def get_downstream_job_names(dom):
    names = [x.text for x in dom.xpath("/root//job/name")]
    ignored_jobs = current_app.config['IGNORED_ISO_JOBS']
    for to_remove in ignored_jobs:
        if to_remove in names:
            names.remove(to_remove)
    return names


def convert_dom_elements(elements):
    result = {}
    for e in elements:
        tag = e.tag
        if tag in mapping.keys():
            f = mapping[tag]
            result[tag] = f(e.text)
    return result


def get_downsteram_builds(dom):
    res = dom.xpath("/root/builds/build")
    builds = {}

    for r in res:
        elements = r.xpath('*')
        parsed = convert_dom_elements(elements)
        number = parsed['number']

        builds[number] = {
            'result': parsed['result'],
            'upstreamProject': parsed['upstreamProject'],
            'upstreamBuild': parsed['upstreamBuild']
        }

    return builds


def extract_urls(text):
    iso, torrent = None, None

    if text:
        urls = util.find_urls(text)
        iso = util.try_index(urls, 0)
        torrent = util.try_index(urls, 1)

    return iso, torrent


def get_upstream_builds(dom):
    res = dom.xpath("/root/builds/build")
    builds = {}

    for r in res:
        elements = r.xpath('*')
        parsed = convert_dom_elements(elements)

        number = parsed['number']
        iso, torrent = extract_urls(parsed['description'])
        date = util.try_read_timestamp(parsed['timestamp']/1000)

        builds[number] = {
            'result': parsed['result'],
            'date': date,
            'iso': iso,
            'torrent': torrent
        }

    return builds


def find_result(downstream_builds, upstream_build_number):
    # {128: {'upstreamBuild': 137,
    #        'result': 'SUCCESS',
    #        'upstreamProject': '6.1.all'}}
    num, result = None, None
    for k, v in downstream_builds.items():
        if v['upstreamBuild'] == upstream_build_number:
            num, result = k, v['result']

    return num, result


def get_iso_info(jenkins_url, job):
    dom = get_dom(jenkins_url, job)
    upstream_builds = get_upstream_builds(dom)

    downstream_job_names = get_downstream_job_names(dom)

    downstream_results = {}
    for job in downstream_job_names:
        job_dom = get_dom(jenkins_url, job)
        builds = get_downsteram_builds(job_dom)

        downstream_results[job] = builds

    for build, data in upstream_builds.items():
        # build = 39, data = {'result': 'SUCCESS'}
        data['downstream'] = {}
        for job in downstream_job_names:
            num, result = find_result(downstream_results[job], build)
            # num = 1, result = 'SUCCESS'
            data['downstream'][job] = {
                'number': num,
                'result': result
            }

    return upstream_builds


def crawl_stable_ci(ci):
    jenkins_url = ci["JENKINS"]
    iso_versions = ci["ISO_JOBS"]

    for iso in iso_versions:
        log.info("Getting ISO build history for {0}".format(iso))
        job = "{0}.all".format(iso)
        builds = get_iso_info(jenkins_url, job)
        db.insert_iso_builds(job, builds)
        log.info("Finished getting ISO build history for {0}".format(iso))


def crawl_master_ci(ci):
    jenkins_url = ci["JENKINS"]
    iso_versions = ci["ISO_JOBS"]

    for iso in iso_versions:
        log.info("Getting ISO build history for {0}".format(iso))
        job = "{0}.all".format(iso)
        builds = iso2.get_iso_info(jenkins_url, iso)
        db.insert_iso_builds(job, builds)
        log.info("Finished getting ISO build history for {0}".format(iso))


def crawl():
    crawl_stable_ci(current_app.config["STABLE_CI"])
    crawl_master_ci(current_app.config["MASTER_CI"])
