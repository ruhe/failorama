import logging
import sys

import click

from crawler import staging
from crawler import iso

from jenkins_reporting import application
from jenkins_reporting import db
from jenkins_reporting.extensions import db as flask_db

log = logging.getLogger(__name__)


def _create_app():
    conf = 'jenkins_reporting.config.Production'
    return application.create_app(conf)


@click.group()
def cli():
    pass


def _query_table_names(app):
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite://'):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
    else:
        query = "SHOW TABLES;"
    return {t[0] for t in flask_db.session.execute(query)}


@cli.command()
def syncdb():
    app = _create_app()
    print "Going to synchronize DB schema."
    with app.app_context():
        tables_before = _query_table_names(app)
        db.init_db()
        tables_after = _query_table_names(app)

    created_tables = tables_after - tables_before
    for table in created_tables:
        log.info("syncdb: Created table {0}".format(table))

    log.info("syncdb: finished")


@cli.command()
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=5000)
def devserver(host, port):
    app = _create_app()
    app.run(host=host, port=port)


@cli.command('update-staging')
def crawl_staging_jobs():
    app = _create_app()
    with app.app_context():
        staging.crawl()


@cli.command('update-iso')
def crawl_iso_jobs():
    app = _create_app()
    with app.app_context():
        iso.crawl()


if __name__ == '__main__':
    logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG,
                        format=logging_format)
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    cli()
