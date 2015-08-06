import datetime
import time

from flask import current_app as app

from crawler import jenkins
from crawler import launchpad
from jenkins_reporting import db




def _get_stop_line():
    now = datetime.date.today()
    week_ago = now - datetime.timedelta(days=7)

    ts = time.mktime(week_ago.timetuple())
    return int(ts)


def scan_failed_builds(job_name):
    jenkins_url = app.config['PRODUCT_JENKINS']
    failed = jenkins.get_builds(jenkins_url, job_name, stopline=_get_stop_line())

    for build in failed:
        build['bugs'] = map(launchpad.get_bug, build['bugs'])

    return failed


def crawl_job(job_name):
    res = scan_failed_builds(job_name)
    db.insert_staging_builds(job_name, res)


def crawl():
    for job in app.config['STAGING_JOBS']:
        print "Starting to crawl job #{0}".format(job)
        crawl_job(job)
        print "Done crawling job #{0}".format(job)
