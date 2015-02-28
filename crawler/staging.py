from flask import current_app as app

from crawler import jenkins
from crawler import launchpad
from jenkins_reporting import db


def scan_failed_builds(job_name):
    jenkins_url = app.config['PRODUCT_JENKINS']
    failed = jenkins.get_failed_builds(jenkins_url, job_name)

    for build in failed:
        build['bugs'] = map(launchpad.get_bug, build['bugs'])
        print('.'),

    print
    return failed


def crawl_job(job_name):
    res = scan_failed_builds(job_name)
    db.insert_staging_builds(job_name, res)


def crawl():
    for job in app.config['STAGING_JOBS']:
        print "Starting to crawl job #{0}".format(job)
        crawl_job(job)
        print "Done crawling job #{0}".format(job)
