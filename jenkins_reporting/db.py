import json

from sqlalchemy.sql.expression import desc

from jenkins_reporting.extensions import db


class JsonEncoded(db.TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class StagingBuild(db.Model):
    __tablename__ = 'staging_builds'

    __table_args__ = (
        db.UniqueConstraint('number', 'job'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer)
    job = db.Column(db.String(100), index=True)
    payload = db.Column(JsonEncoded())

    def __repr__(self):
        return "#{0} {1}".format(self.number, self.job)


class IsoBuild(db.Model):
    __tablename__ = 'iso_builds'

    __table_args__ = (
        db.UniqueConstraint('number', 'job'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer())
    result = db.Column(db.String(20))
    date = db.Column(db.DateTime())
    job = db.Column(db.String(100), index=True)
    iso_url = db.Column(db.String(200))
    torrent_url = db.Column(db.String(200))
    downstream = db.Column(JsonEncoded())

    def __repr__(self):
        return "[{0}] #{1} {2} {3}".format(self.result, self.number,
                                           self.job, self.downstream)


def init_db():
    db.create_all()


def get_staging_builds(job):
    res = StagingBuild.query.filter_by(job=job).\
        order_by(desc(StagingBuild.number)).all()
    return [x.payload for x in res]


def insert_staging_builds(job, builds):
    for b in builds:
        build = StagingBuild.query.\
            filter_by(number=b['number'], job=job).first()
        new_build = StagingBuild(number=b['number'], job=job, payload=b)

        if build:
            new_build.id = build.id
            db.session.merge(new_build)
        else:
            db.session.add(new_build)

    db.session.commit()


def get_iso_builds(job):
    return IsoBuild.query.filter_by(job=job).\
        order_by(desc(IsoBuild.number)).all()


def insert_iso_builds(job, builds):
    for number, values in builds.items():
        build = IsoBuild.query.filter_by(number=number, job=job).first()
        new_build = IsoBuild(number=number,
                             result=values['result'],
                             date=values['date'],
                             job=job,
                             iso_url=values['iso'],
                             torrent_url=values['torrent'],
                             downstream=values['downstream'])

        if build:
            new_build.id = build.id
            db.session.merge(new_build)
        else:
            db.session.add(new_build)

    db.session.commit()
