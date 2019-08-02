import functools
import json
import os
from pprint import pprint

import flask
from flask import (Blueprint, abort, current_app, flash, jsonify,
                   make_response, redirect, render_template, request, url_for)
from flask_cors import CORS
from flask_dance.contrib.google import google, make_google_blueprint
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2.rfc6749.errors import (InvalidClientIdError,
                                            TokenExpiredError,
                                            InvalidGrantError)

from fet_api_to_gcal import config
from fet_api_to_gcal.common.utils import getDate, login_required

app = flask.Flask(__name__)
app.config.from_object(config.DevelopmentConfig)

CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# security params config

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

CLIENT_ID = "991974833650-r66aqfg60ga0f8oj2itrgghf4hvt8qs0.apps.googleusercontent.com"
CLIENT_SECRET = "1SaQh1nxJ1A9EUsID6EIWoVy"
app.config["GOOGLE_OAUTH_CLIENT_ID"] = CLIENT_ID
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = CLIENT_SECRET
google_bp = make_google_blueprint(
    scope=["profile", "email", "https://www.googleapis.com/auth/calendar"],
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    offline=True)
app.register_blueprint(google_bp, url_prefix="/login")

from fet_api_to_gcal.models import Calendar, Demande, Resource, User, Teacher, events__log, Std_mail


@app.route('/resources/import', methods=["GET"])
@login_required(google)
def add_resources_to_db():
    f = open("resources.json", 'r')
    resources_json = json.load(f)
    for resource in resources_json['items']:
        res = Resource(name=str(resource["generatedResourceName"]),
                       resource_email=str(resource["resourceEmail"]),
                       capacity=int(resource["capacity"]))
        queried_resource = Resource.query.filter_by(
            resource_email=resource["resourceEmail"]).first()
        if queried_resource is None:
            db.session.add(res)
        else:
            pass
    db.session.commit()
    f.close()
    return jsonify({"status": "done"})


@app.route("/salles")
@login_required(google)
def salles():
    return make_response(render_template('salle.html'), 200)


@app.route("/")
@login_required(google)
def index():
    if not google.authorized:
        return flask.redirect(url_for("google.login"))
    else:
        #resp = google.get()
        user_data = {
            "name": flask.session["name"],
            "email": flask.session["account"]
        }
        return render_template('index.html.j2', user_data=user_data)
    #resp = google.get("/calendar/v3/users/me/calendarList")
    #return jsonify(resp.json())


@app.route('/logout')
@login_required(google)
def logout():
    """Revokes token and empties session"""
    if google.authorized:
        try:
            google.get(
                'https://accounts.google.com/o/oauth2/revoke',
                params={
                    'token':
                    current_app.blueprints['google'].token['access_token']
                },
            )
        except TokenExpiredError:
            return redirect(url_for("google.login"))
        except InvalidGrantError:
            return redirect(url_for("index"))
        except InvalidClientIdError:
            pass
    flask.session.clear()
    return redirect(url_for('index'))


@app.errorhandler(InvalidClientIdError)
def token_expired(_):
    del current_app.blueprints['google'].token
    flash('Your session has expired. Please submit the request again', 'error')
    return redirect(url_for('index'))


@app.errorhandler(InvalidGrantError)
def invalid_grant(_):
    def current_app.blueprints['google'].token
    flash("InvalidGrant Error", category="error")
    return redirect(url_for('index'))



@app.route("/api/v1/calendars")
@login_required(google)
def calendars():
    if not google.authorized:
        return flask.redirect(url_for("google.login"))

    resp = google.get("/calendar/v3/users/me/calendarList")
    json_resp = resp.json()
    calendars = []
    for i in json_resp["items"]:
        calendars.append({
            "name": i["summary"],
            "id": i["id"],
            "accessRole": i["accessRole"]
        })

    return jsonify(calendars)


@app.route('/api/v1/calendar/add/<str:calendar_name>')
@login_required(google)
def new_calendar():
    if not google.authorized:
        return flask.redirect(url_for('google.login'))

    calendar__ = {'summary': 'New_calendar', 'timeZone': 'Africa/Algiers'}

    resp = google.post("/calendar/v3/calendars", json=calendar__)

    return resp.json()


@app.route('/api/v1/events/add/<int:ev_num>')
@login_required(google)
def event_add():
    calendar_id = "esi.dz_tsek485jfut3vqt7kjf4c2vogg@group.calendar.google.com"
    f = open("out.json", 'r')
    json_tt = json.load(f)
    for event_id in range(5):
        event = json_tt[event_id]
        resp = google.post(
            "/calendar/v3/calendars/{}/events".format(calendar_id), json=event)

    return resp.json()


@app.route("/api/v1/events/latest/<int:number_of_events>")
@login_required(google)
def delete_latest_events(number_of_events):
    pass


@app.route("/api/v1/convert/json")
def csv_tt_to_json_events(
        filename="fet_api_to_gcal/data/ESI_2019_01_10_14v7_timetable.csv"):
    dates = {
        "1CPI": "2019/08/01",
        "2CPI": "2019/08/02",
        "1CS": "2019/08/02",
        "2CS": "2019/08/02",
        "3CS": "2019/08/02"
    }
    events_freq = 1
    timezone = "Africa/Algiers"
    f = open(filename, "r")
    lines = f.readlines()[1::]
    all_events = []  # to hold all json gevents later!
    temp_dict_holder = {}
    for line in lines:
        line_splitted = list(
            map(lambda x: x.replace('"', ''),
                line.strip().split(",")))[:-1]
        if "Pause" not in line_splitted[2]:
            if line_splitted[0] not in list(temp_dict_holder.keys()):
                start_end = line_splitted[2].split("-")
                temp_dict_holder[line_splitted[0]] = {
                    "Day":
                    line_splitted[1],
                    "start":
                    start_end[0],
                    "end":
                    start_end[1],
                    "teachers":
                    line_splitted[5].split("+"),
                    "room":
                    line_splitted[-1],
                    "summary":
                    "{} {} {}".format(line_splitted[-2], line_splitted[-4],
                                      line_splitted[-3]),
                    "std_set":
                    line_splitted[3]
                }
            else:
                temp_dict_holder[
                    line_splitted[0]]["end"] = line_splitted[2].split("-")[1]
        else:
            continue

    # 2nd phase
    for event_inx in range(1, len(temp_dict_holder) + 1):
        try:
            event___old = temp_dict_holder[str(event_inx)]
        except KeyError as e:
            continue
        __gevent__ = {"summary": event___old["summary"]}

        # get attendees emails
        __gevent__["attendees"] = []
        # teachers
        for teacher_name in event___old["teachers"]:
            teacher = Teacher.query.filter_by(fet_name=teacher_name).first()
            if teacher is not None:
                __gevent__["attendees"].append(
                    {"email": teacher.teacher_email})
        # students
        if event___old["std_set"] == "":
            print("WTF")
            continue
        for std_set__ in event___old["std_set"].split("+"):

            std_mails_obj = Std_mail.query.filter_by(std_set=std_set__).first()
            if std_mails_obj is not None:
                __gevent__["attendees"].append(
                    {"email": std_mails_obj.std_email})

        # add room if existing

        if event___old["room"] != "":
            res = Resource.query.filter_by(
                resource_name=event___old["room"]).first()
            if res is not None:
                __gevent__["attendees"].append({
                    "email": res.resource_email,
                    "resource": True
                })

        # recurrence rule
        __gevent__["recurrence"] = [
            "RRULE:FREQ=WEEKLY;COUNT=" + str(events_freq)
        ]
        # set start and time
        #print(event___old["std_set"].split(" ")[0])
        dateTime_start = getDate(dates, event___old["std_set"].split(" ")[0],
                                 event___old["Day"],
                                 event___old["start"].split("h")[0],
                                 event___old["start"].split("h")[1])
        dateTime_end = getDate(dates, event___old["std_set"].split()[0],
                               event___old["Day"],
                               event___old["end"].split("h")[0],
                               event___old["end"].split("h")[1])
        __gevent__["start"] = {
            "timeZone": timezone,
            "dateTime": dateTime_start,
        }
        __gevent__["end"] = {
            "timeZone": timezone,
            "dateTime": dateTime_end,
        }

        all_events.append(__gevent__)

    return jsonify(all_events)


@app.errorhandler(404)
def page_not_found(e):
    user_data = user_data = {
        "name": flask.session["name"],
        "email": flask.session["account"]
    }
    return make_response(render_template('sorry.html.j2', user_data=user_data),
                         404)
