from flask import current_app as app
import lxml.etree as et

import crawler as current_path
from crawler import util
from jenkins_reporting import application
from jenkins_reporting import db

mapping = {
    'number': util.try_int,
    'result': util.ident,
    'upstreamProject': util.ident,
    'upstreamBuild': util.try_int,
    'description': util.ident,
    'timestamp': util.try_int
}


def build_dom(xml_path, xslt_path):
    dom = et.parse(xml_path)
    xslt = et.parse(xslt_path)
    transform = et.XSLT(xslt)
    return transform(dom)


def get_dom(job):
    jenkins_url = app.config['PRODUCT_JENKINS']
    link = "{0}/job/{1}/api/xml?depth=1".format(jenkins_url, job)

    xslt_path = util.file_abs_path('build.xslt', current_path.__file__)
    return build_dom(link, xslt_path)


def get_downstream_job_names(dom):
    names = [x.text for x in dom.xpath("/root//job/name")]
    ignored_jobs = app.config['IGNORED_ISO_JOBS']
    for to_remove in ignored_jobs:
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
    # {128: {'upstreamBuild': 137, 'result': 'SUCCESS', 'upstreamProject': '6.1.all'}}
    num, result = None, None
    for k, v in downstream_builds.items():
        if v['upstreamBuild'] == upstream_build_number:
            num, result = k, v['result']

    return num, result


def get_iso_info(job):
    dom = get_dom(job)
    upstream_builds = get_upstream_builds(dom)

    downstream_job_names = get_downstream_job_names(dom)

    downstream_results = {}
    for job in downstream_job_names:
        job_dom = get_dom(job)
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


def crawl():
    iso_versions = app.config['ISO_VERSIONS']

    for iso in iso_versions:
        print "Getting ISO build history for {0}".format(iso)
        job = "{0}.all".format(iso)
        builds = get_iso_info(job)
        db.insert_iso_builds(job, builds)
        print "Finished getting ISO build history for {0}".format(iso)
