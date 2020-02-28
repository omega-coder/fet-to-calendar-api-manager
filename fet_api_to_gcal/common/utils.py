#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import ntpath
import re
from functools import wraps

from flask import (current_app, flash, redirect, render_template, session,
                   url_for)



def path_leaf(path):
    """ Cross platform function to get the filename from any path. 
    
    Args:
        path (ste): A string path.
    
    Returns:
        str: the basename of the path
    """    
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def timestamped_filename(filename, fmt='%m-%d-%y-%H:%M:%S-{filename}'):
    """Returns a timestamped log filename used with logging module.
    
    Args:
        filename (str): a string for the filename to be timestamped.
        fmt (str, optional): your timestamping format (No need to change it). Defaults to '%m-%d-%y-%H.%M.%S-{filename}'.
    
    Returns:
        str: a timstamped filename given as parameter.
    """    
    return datetime.datetime.now().strftime(fmt).format(filename=filename)

def login_required(google):
    """Checks that a current user is authneticated with google before allowing the route visit.
    
    Args:
        google (werkzeug.local.LocalProxy): A google local proxy used for google Oauth.
    
    Returns:
        TODO: enchance the Returns documentation.   
        decorated function: decorated route 
    """    
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
    """Returns a combined date-time value (formatted according to RFC3339).
    
    Args:
        dates (dict): a dictionary type key: value with keys corresppnding to the study years
                      and a value corresponding to the starting study date of that year.
                      IMPORTANT: the starting date must correspond the the first day of the week (Sunday).
        promo (str): string of the promotion year.
        day (str): string of the event date (must be in french)
        heure (str): string of the hour of the event
        minute (str): string of the minute after the hour string
    
    Returns:
        str: combined date-time value (formatted according to RFC3339).
    """    
    plus = {"Dimanche": 0, "Lundi": 1, "Mardi": 2, "Mercredi": 3, "Jeudi": 4}
    dt = datetime.datetime.strptime(
        dates[promo], "%Y/%m/%d") + datetime.timedelta(
            days=plus[day], hours=int(heure), minutes=int(minute))
    date_splitted = str(dt).split(" ")
    full_date = date_splitted[0] + "T" + date_splitted[1] + "+01:00"
    return full_date


# print error text
def perror(text):
    """utility to print an error with a red color to stdout
    
    Args:
        text (str): string to be printed.
    """    
    print(bcolors.FAIL + text + bcolors.ENDC)


# print success text
def psuccess(text):
    """utility to print an explicit success with a green color to stdout
    
    Args:
        text (str): string to be printed.
    """    
    print(bcolors.OKGREEN + text + bcolors.ENDC)


def check_google_calendar_id(google_cal_id):
    """utility to verify a google calendar id passed as a parameter. 
    
    Args:
        google_cal_id (str): string of the google calendar id
    
    Returns:
        bool: True if the string in parameter is a verified google calendar id, else returns False 
    """    
    return bool(
        re.match(r"esi\.dz_[a-z0-9]{26}@group\.calendar\.google\.com",
                 google_cal_id))
