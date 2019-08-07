from fet_api_to_gcal import db
from datetime import datetime
import json


class Resource(db.Model):
    __tablename__ = "resources"
    resource_id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(60), index=True, unique=True)
    gen_resource_name = db.Column(db.String(60), index=True, unique=True)
    resource_email = db.Column(db.String(100), index=True, unique=True)
    capacity = db.Column(db.Integer, nullable=True)
    building = db.Column(db.String(100), index=True)

    def __repr__(self):
        return "{}".format(self.name)


class Demande(db.Model):
    __tablename__ = "demandes"
    demande_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    state = db.Column(db.Boolean, index=True, default=0)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    req_resource = db.Column(db.String(60), index=True, nullable=True)

    def __repr__(self):
        return json.dumps({
            "requested": self.req_resource,
            "from": self.start_time,
            "to": self.end_time
        })


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True)
    email = db.Column(db.String(100), unique=True, index=True)

    def __repr__(self):
        return json.dumps({"name": self.name, "email": self.email})


class Calendar(db.Model):
    __tablename__ = "calendars"
    id = db.Column(db.Integer, primary_key=True)
    calendar_id_google = db.Column(db.String(100), unique=True, index=True)
    summary = db.Column(db.String(100), unique=True)
    std_email = db.Column(db.String(100), unique=True, index=True)

    def __repr__(self):
        return json.dumps({
            "name": self.summary,
            "calendar_id": self.calendar_id_google
        })


class import_oprtation(db.Model):
    __tablename__ = "import_ops"
    id = db.Column(db.Integer, primary_key=True)
    import_date = db.Column(db.DateTime, default=datetime.utcnow())
    filename = db.Column(db.String(100))
    number_events = db.Column(db.Integer)


class events__log(db.Model):
    __tablename__ = "events__log"
    id = db.Column(db.Integer, primary_key=True)
    gevent_id = db.Column(db.String(100), unique=True)
    gcalendar_id = db.Column(db.String(100), index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    import_id = db.Column(db.Integer, db.ForeignKey('import_ops.id'))
    import_ops = db.relationship("import_oprtation",
                                 backref=db.backref("import_ops",
                                                    uselist=False))

    def __repr__(self):
        json.dumps({
            "added_at": self.added_at,
            "gevent_id": self.gevent_id,
            "gcalendar_id": self.gcalendar_id,
        })


class Std_mail(db.Model):
    __tablename__ = "std_mails"
    mail_id = db.Column(db.Integer, primary_key=True)
    std_set = db.Column(db.String(20), index=True, unique=True, nullable=False)
    std_email = db.Column(db.String(100),
                          index=True,
                          unique=True,
                          nullable=False)

    def __repr__(self):
        return json.dumps({
            "std_set": self.std_set,
            "std_email": self.std_email
        })


class Teacher(db.Model):
    __tablename__ = "teachers"
    teacher_id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(60))
    teacher_email = db.Column(db.String(100), unique=True, index=True)
    fet_name = db.Column(db.String(40))

    def __repr__(self):
        return json.dumps({
            "teacher_fet_name": self.fet_name,
            "std_email": self.teacher_email
        })
