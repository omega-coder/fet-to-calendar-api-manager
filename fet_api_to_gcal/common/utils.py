#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import (flash, redirect, url_for, render_template, session,
                   current_app)

from functools import wraps
import datetime
import re


def login_required(google):
    """Enforces authentication on a route"""
    def decorated(func):
        @wraps(func)
        def decorated_route(*args, **kwargs):
            if not google.authorized:
                return redirect(url_for("google.login"))

            if not all(key in session for key in ['domain', 'account']):
                resp = google.get('/userinfo/v2/me')
                if resp.status_code != 200:
                    flash(
                        'Could not get your profile informations from google',
                        category='danger')
                    return render_template('sorry.html.j2'), 403

                body = resp.json()
                if not all(v in body.keys() for v in ['hd', 'email']):
                    flash((
                        'Incomplete profile informations was returned by google'
                    ),
                          category='danger')
                    return render_template('sorry.html.j2'), 403
                session['domain'] = body['hd']
                session['account'] = body['email']
                session['name'] = body['name']
                session["picture"] = body["picture"]
            if session['domain'] in current_app.config["DOMAIN_WHITELIST"]:
                if session["account"] not in current_app.config[
                        "EMAIL_WHITELIST"]:
                    flash((
                        'The account you are logged in with does not match the'
                        'configured whitelist'),
                          category="danger")
                    session.clear()
                    return render_template('sorry.html.j2'), 403
                return func(*args, **kwargs)
            flash(('The account you are logged in with does not match the '
                   'configured whitelist'),
                  category='danger')
            return render_template('sorry.html.j2'), 403

        return decorated_route

    return decorated


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def getDate(dates, promo, day, heure, minute):
    plus = {"Dimanche": 0, "Lundi": 1, "Mardi": 2, "Mercredi": 3, "Jeudi": 4}
    dt = datetime.datetime.strptime(
        dates[promo], "%Y/%m/%d") + datetime.timedelta(
            days=plus[day], hours=int(heure), minutes=int(minute))
    date_splitted = str(dt).split(" ")
    full_date = date_splitted[0] + "T" + date_splitted[1] + "+01:00"
    return full_date


# print error text
def perror(text):
    print(bcolors.FAIL + text + bcolors.ENDC)


# print success text
def psuccess(text):
    print(bcolors.OKGREEN + text + bcolors.ENDC)


def check_google_calendar_id(google_cal_id):
    return bool(
        re.match(r"esi\.dz_[a-z0-9]{26}@group\.calendar\.google\.com",
                 google_cal_id))
