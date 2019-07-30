import functools
import os
import flask
from flask_cors import CORS
from flask import url_for, redirect, request, abort, render_template, Blueprint, flash, current_app
from fet_api_to_gcal import config
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError, TokenExpiredError
from pprint import pprint
from flask import jsonify


app = flask.Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
CORS(app)

CLIENT_ID = "991974833650-r66aqfg60ga0f8oj2itrgghf4hvt8qs0.apps.googleusercontent.com"
CLIENT_SECRET = "1SaQh1nxJ1A9EUsID6EIWoVy"

app.config["GOOGLE_OAUTH_CLIENT_ID"] = CLIENT_ID
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = CLIENT_SECRET


google_bp = make_google_blueprint(scope=["profile", "email", "https://www.googleapis.com/auth/calendar"],
                                    client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
app.register_blueprint(google_bp, url_prefix="/login")



@app.route("/")
def index():
    if not google.authorized:
        return flask.redirect(url_for("google.login"))


    resp = google.get("/calendar/v3/users/me/calendarList")
    return jsonify(resp.json())


@app.route('/logout')
def logout():
    """Revokes token and empties session"""
    if google.authorized:
        try:
            google.get(
                'https://accounts.google.com/o/oauth2/revoke',
                params={
                    'token': current_app.blueprints['google'].token['access_token']
                },
            )
        except TokenExpiredError:
            pass
        except InvalidClientIdError:
            pass
    flask.session.clear()
    return redirect(url_for('index'))


@app.errorhandler(InvalidClientIdError)
def token_expired(_):
    del current_app.blueprints['google'].token
    flash('Your session has expired. Please submit the request again', 'error')
    return redirect(url_for('index'))



@app.route("/api/v1/calendars")
def calendars():
    if not google.authorized:
        return flask.redirect(url_for("google.login"))

    resp = google.get("/calendar/v3/users/me/calendarList")
    json_resp = resp.json()
    calendars = []
    for i in json_resp["items"]:
        calendars.append({"name": i["summary"], "id": i["id"], "accessRole": i["accessRole"]})

    return jsonify(calendars)


@app.route('/api/v1/calendar/add')
def new_calendar():
    if not google.authorized:
        return flask.redirect(url_for('google.login'))

    calendar__ = {
        'summary': 'New_calendar',
        'timeZone': 'Africa/Algiers'
    }

    resp = google.post("/calendar/v3/calendars", json=calendar__)

    return resp.json()

@app.route('/api/v1/events/add')
def event_add():
    calendar_id = "esi.dz_tsek485jfut3vqt7kjf4c2vogg@group.calendar.google.com"
    event = {
        'summary': "Sample Event",
        'location': '1337 location',
         'start': {
                'dateTime': '2019-07-30T09:00:00-07:00',
                'timeZone': 'Africa/Algiers',
          },
          'end': {
            'dateTime': '2019-07-30T17:00:00-07:00',
            'timeZone': 'Africa/Algiers',
          },
    }

    resp = google.post("/calendar/v3/calendars/{}/events".format(calendar_id), json=event)

    return resp.json()
