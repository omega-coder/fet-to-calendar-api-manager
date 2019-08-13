import functools
import json
import os
from pprint import pprint
from time import sleep
import flask
from flask import (Blueprint, abort, current_app, flash, jsonify,
                   make_response, redirect, render_template, request, url_for)
from flask_cors import CORS
from flask_dance.contrib.google import google, make_google_blueprint
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2.rfc6749.errors import (InvalidClientIdError,
                                            TokenExpiredError,
                                            InvalidGrantError,
                                            UnauthorizedClientError)
from fet_api_to_gcal import config
from fet_api_to_gcal.common.utils import getDate, login_required
from werkzeug.utils import secure_filename

app = flask.Flask(__name__)
app.config.from_object(config.DevelopmentConfig)

CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ALLOWED EXTENSIONS IN UPLOADS
ALLOWED_EXTENSIONS = set(['csv'])
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


# SECURITY params config

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

from fet_api_to_gcal.models import Calendar, Demande, Resource, User, Teacher, events__log, Std_mail, import_oprtation


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
    all_events = csv_tt_to_json_events(max_events=500)
    return jsonify(all_events)


@app.route("/")
@login_required(google)
def index():
    if not google.authorized:
        return flask.redirect(url_for("google.login"))
    else:
        user_data = {
            "name": flask.session["name"],
            "email": flask.session["account"]
        }
        flash(("You are logged in as {}".format(user_data["email"])),
              category='success')
        return render_template('index.html.j2', user_data=user_data)


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
        except UnauthorizedClientError:
            flask.session.clear()
            return redirect(url_for("google.login"))
        except TokenExpiredError:
            flask.session.clear()
            return redirect(url_for("google.login"))
        except InvalidGrantError:
            flask.session.clear()
            return redirect(url_for("google.login"))
        except InvalidClientIdError:
            flask.session.clear()
            return redirect(url_for('google.login'))
    return redirect(url_for('google.login'))


@app.errorhandler(InvalidClientIdError)
def token_expired(_):
    del current_app.blueprints['google'].token
    flash('Your session has expired. Please submit the request again',
          'danger')
    return redirect(url_for('index'))


@app.errorhandler(InvalidGrantError)
def invalid_grant(_):
    del current_app.blueprints['google'].token
    flash(("InvalidGrant Error"), category="danger")
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


@app.route('/api/v1/events/add/<int:ev_num>')
@login_required(google)
def event_add():
    calendar_id = "esi.dz_kqcdeugtt1lgnpms6htbotmigg@group.calendar.google.com"
    f = open("out.json", 'r')
    json_tt = json.load(f)
    for event_id in range(5):
        event = json_tt[event_id]
        resp = google.post(
            "/calendar/v3/calendars/{}/events".format(calendar_id), json=event)

    return resp.json()


@app.route("/api/v1/events/latest/<int:number_of_events>",
           methods=["GET", "DELETE"])
@login_required(google)
def delete_latest_events(number_of_events):
    pass


@app.route("/calendars/<string:calendar_id>/events/<string:event_id>",
           methods=["GET", "DELETE"])
@login_required(google)
def delete_event(calendar_id, event_id):
    if request.method == "DELETE":
        resp = google.delete("/calendar/v3/calendars/{}/events/{}/".format(
            calendar_id, event_id))
        if 200 <= resp.status_code < 300:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "failed"})
    elif request.method == "GET":
        resp = google.get("/calendar/v3/calendars/{}/events/{}/".format(
            calendar_id, event_id))
        if resp.status_code == 200:
            return jsonify(resp.json()), 200
        else:
            return jsonify({"status": "failed"}), resp.status_code


@app.route("/operation/delete/<int:id_import>", methods=["GET"])
@login_required(google)
def delete_importation(id_import):
    events = events__log.query.filter_by(import_id=id_import).all()
    for event in events:
        event_id = event.gevent_id
        gcalendar_id = event.gcalendar_id
        resp = google.delete("/calendar/v3/calendars/{}/events/{}/".format(
            gcalendar_id, event_id))
        if resp.status_code == 204:
            db.session.delete(event)
    import_op = import_oprtation.query.filter_by(id=id_import).first()
    db.session.delete(import_op)
    db.session.commit()
    flash(("Operation {} deleted successfully".format(id_import)),
          category="success")
    return redirect(url_for('operations')), 302


@app.route("/operations", methods=["GET"])
@login_required(google)
def operations():
    if request.method == "GET":
        try:
            operations = db.session.query(import_oprtation).order_by(
                import_oprtation.id.desc()).all()
        except Exception as e:
            flash(("{}".format(e)), category="danger")
            return render_template('operations.html.j2',
                                   operations=None,
                                   title="Operations"), 200
        return render_template('operations.html.j2',
                               operations=operations,
                               title="Operations"), 200


def get_buildings():
    return [str(b[0]) for b in db.session.query(Resource.building).distinct()]


@app.route("/teacher/add", methods=["POST"])
@login_required(google)
def teacher_add_to_db():
    if request.method == "POST":
        fet_name = request.form["fet_name"]
        fullname = request.form["fullname"]
        teacher_email = request.form["t_email"]
        try:
            teacher_obj = Teacher(teacher_email=teacher_email, fet_name=fet_name, fullname=fullname)
            db.session.add(teacher_obj)
            db.session.commit()
            flash(("Teacher {} added successfully.".format(fet_name)), category="success")
            return redirect(url_for('teacher_list')), 302
        except Exception as e:
            flash("Exception: {}".format(str(e)), category="danger")
            return redirect(url_for("teacher_list")), 302


@app.route("/teacher/edit/<int:teacher_id>", methods=["GET", "POST"])
@login_required(google)
def edit_teacher(teacher_id):
    if request.method == "POST":
        pass
    elif request.method == "GET":
        pass

        

@app.route("/teacher/delete/<int:teacher_id>", methods=["GET"])
@login_required(google)
def delete_teacher(teacher_id):
    try:
        teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
        db.session.delete(teacher)
        db.session.commit()
        flash(("Teacher {} deleted successfully.".format(teacher.fet_name)), category="success")
        return redirect(url_for('teacher_list')), 302
    except Exception as e:
        flash(("Sorry: {}".format(str(e))), category="danger")
        return redirect(url_for('teacher_list')), 302


@app.route("/teachers", methods=["GET"])
@login_required(google)
def teacher_list():
    if request.method == "GET":
        # get all teacher records from teachers tablename
        try:
            teachers = db.session.query(Teacher).order_by(Teacher.teacher_id.asc()).all()
            flash(('Fetched {} teachers from database'.format(len(teachers))), category="info")
            return render_template('teachers.html.j2', teachers=teachers)
        except Exception as e:
            print(e)
            flash(("{}".format(str(e))), category="danger")
            return redirect(request.url), 302


@app.route("/import", methods=["GET", "POST"])
@login_required(google)
def import_csv_to_calendar_api():
    if request.method == "GET":
        return make_response(render_template('import.html.j2'), 200)
    elif request.method == "POST":
        max_events = int(request.form["max_events"])
        calendar_id = "esi.dz_kqcdeugtt1lgnpms6htbotmigg@group.calendar.google.com"
        if 'file' not in request.files:
            flash(("No file part"), category='danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == "":
            flash("No file selected for uploading", category='danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file__path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file__path)

            operation_now = import_oprtation(number_events=max_events,
                                             filename=filename)
            db.session.add(operation_now)
            try:
                op_id = db.session.query(import_oprtation).order_by(
                    import_oprtation.id.desc()).first().id
            except Exception as e:
                print(e)

            all_events = csv_tt_to_json_events(file__path,
                                               max_events=max_events)
            for event in all_events:
                for std_mail in event["attendees"][1:-1]:
                    cal_rec = Calendar.query.filter_by(
                        std_email=std_mail["email"]).first()
                    if cal_rec:
                        calendar_id = cal_rec.calendar_id_google
                    else:
                        print("could not add event, continuing to next event")
                        continue
                    resp = google.post(
                        "/calendar/v3/calendars/{}/events".format(calendar_id),
                        json=event)
                    if resp.status_code == 200:
                        gevent_id = resp.json()["id"]
                        event = events__log(gevent_id=gevent_id,
                                            gcalendar_id=calendar_id,
                                            import_id=op_id)
                        try:
                            db.session.add(event)
                        except Exception as e:
                            print(e)
                    else:
                        print("Could not insert event")
            db.session.commit()

            flash(("Added {} events to calendar".format(len(all_events))),
                  category='success')
            return redirect(url_for('import_csv_to_calendar_api'))
        else:
            flash('Allowed file types are: csv', category="info")
            return redirect(request.url)


@app.route("/calendars", methods=["GET"])
@login_required(google)
def get_calendars():
    if request.method == "GET":
        try:
            calendars = db.session.query(Calendar).order_by(Calendar.id).all()
        except Exception as e:
            flash(("{}".format(e)), category="danger")
            return render_template('calendars.html.j2',
                                   calendars=None,
                                   title="Calendars"), 200
        return render_template('calendars.html.j2',
                               calendars=calendars,
                               title="Calendars"), 200


def new_calendar(calendar_name):
    if google.authorized:
        calendar__ = {'summary': calendar_name, 'timeZone': 'Africa/Algiers'}
        resp = google.post("/calendar/v3/calendars", json=calendar__)
        if resp.status_code == 200:
            return resp.json()["id"]
        else:
            print(resp.json())
            return None
    else:
        return None


@app.route("/calendar/delete/<string:gcalendar_id>")
@login_required(google)
def delete_calendar(gcalendar_id):
    return render_template('calendars.html.j2',
                           title="Calendars opearations"), 200


@app.route("/api/v1/calendar/add/<string:summary>/<string:std_email>")
@login_required(google)
def add_calendar(summary, std_email):
    cal_record = Calendar.query.filter_by(summary=summary).first()
    if cal_record is None:
        calendar__ = {'summary': summary, 'timeZone': 'Africa/Algiers'}
        resp = google.post("/calendar/v3/calendars", json=calendar__)
        if resp.status_code == 200:
            calendar_id = resp.json()["id"]
        else:
            print(resp.json())
            calendar_id = None
        if calendar_id is not None:
            cal_rec = Calendar(calendar_id_google=calendar_id,
                               summary=summary,
                               std_email=std_email)
            db.session.add(cal_rec)
    else:
        print(cal_record)
    db.session.commit()
    if calendar_id:
        return jsonify(resp.json()), 200
    else:
        return jsonify({"status": "failed"}), 200

@app.route("/calendar/add", methods=["POST"])
@login_required(google)
def calendar_add():
   calendar_name = request.form["calendar_name"]
   std_email = request.form["std_email"]

   cal_record = Calendar.query.filter_by(summary=calendar_name).first() 
   if cal_record is None:
        calendar__ = {'summary': calendar_name, 'timeZone': 'Africa/Algiers'}
        resp = google.post("/calendar/v3/calendars", json=calendar__)
        if resp.status_code == 200:
            if "id" in resp.json().keys():
                calendar_id = resp.json()["id"]
                calendar_obj = Calendar(calendar_id_google=calendar_id, summary=calendar_name, std_email=std_email)
                db.session.add(calendar_obj)
                db.session.commit()
                flash(('Added calendar {} to both google calendar and local database'.format(calendar_name)), category="success")
                return redirect(url_for("get_calendars"))
            else:
                flash(("Invalid response from calendar api"), category="danger")
                return redirect(url_for('get_calendars')), 302
        else:
            flash(("Calendar API returned a non 200 response"), category="danger")
            return redirect(url_for('get_calendars')), 302
   else:
        flash(("Calendar {} already found in application database".format(calendar_name)), category="info")
        return redirect(url_for('get_calendars')), 302





@app.route("/calendars/import", methods=["GET", "POST"])
@login_required(google)
def import_calendars():
    if request.method == "GET":
        return render_template('calendars_import.html.j2',
                               title='Import Calendars')
    elif request.method == "POST":
        if 'file' not in request.files:
            flash(("No file part"), category='danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == "":
            flash("No file selected for uploading", category='danger')
            return redirect(request.url)
        added_calendars = 1  # number of added calendars
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file__path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            for line in file.readlines():
                line = line.decode().strip().split(",")
                cal_record = Calendar.query.filter_by(summary=line[0]).first()
                print(cal_record)
                if cal_record is None:
                    calendar__ = {
                        'summary': line[0],
                        'timeZone': 'Africa/Algiers'
                    }
                    resp = google.post("/calendar/v3/calendars",
                                       json=calendar__)
                    if resp.status_code == 200:
                        calendar_id = resp.json()["id"]
                    else:
                        print(resp.json())
                        calendar_id = None
                    sleep(5)
                    if calendar_id is not None:
                        cal_rec = Calendar(calendar_id_google=calendar_id,
                                           summary=line[0],
                                           std_email=line[1].replace('"', ''))
                        db.session.add(cal_rec)
                        added_calendars += 1
            db.session.commit()
            flash(("Added {} calendars to google calendar from file {}".format(
                added_calendars, filename)),
                  category="success")
            return redirect(request.url), 302
        else:
            flash(("[ERROR] File is not allowed"), category="danger")
            return render_template('calendars_import.html.j2'), 200


def csv_tt_to_json_events(
        filename="fet_api_to_gcal/data/ESI_2019_01_10_14v7_timetable.csv",
        events_freq=1,
        max_events=None):
    dates = {
        "1CPI": "2019/08/02",  # needs to be changed!
        "2CPI": "2019/08/02",  # needs to be changed!
        "1CS": "2019/08/02",  # needs to be changed!
        "2CS": "2019/08/02",  # needs to be changed!
        "3CS": "2019/08/02"  # needs to be changed!
    }

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
        if len(all_events) == max_events:
            return all_events
    return all_events


@app.errorhandler(404)
def page_not_found(e):
    user_data = user_data = {
        "name": flask.session["name"],
        "email": flask.session["account"]
    }
    return make_response(render_template('404.html.j2', user_data=user_data),
                         404)
