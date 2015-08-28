import logging

from flask import current_app

from crawler import jenkins
from crawler import launchpad
from crawler import util
from jenkins_reporting import db

log = logging.getLogger(__name__)


def scan_failed_builds(jenkins_url, job_name):
    failed = jenkins.get_builds(jenkins_url,
                                job_name,
                                stopline=util.days_ago_timestamp(7))

    for build in failed:
        build['bugs'] = map(launchpad.get_bug, build['bugs'])

    return failed


def crawl_job(jenkins_url, job_name):
    res = scan_failed_builds(jenkins_url, job_name)
    db.insert_staging_builds(job_name, res)


def crawl_ci(ci):
    jenkins_url = ci["JENKINS"]
    staging_jobs = ci["STAGING_JOBS"]

    for job in staging_jobs:
        log.info("Starting to crawl job #{0}".format(job))
        crawl_job(jenkins_url, job)
        log.info("Done crawling job #{0}".format(job))


def crawl():
    crawl_ci(current_app.config["MASTER_CI"])
    crawl_ci(current_app.config["STABLE_CI"])
