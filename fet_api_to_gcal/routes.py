from flask import url_for, redirect, request, abort, render_template
from fet_api_to_gcal import app
from googleapiclient import discovery
from google.auth import OAuth2Session

@app.route("/api/v1/test")
@app.route("/test")
def test():
    return {"name": "test"}


@app.route("/api/v1/login", methods=["GET"])
@no_cache
def login():
    pass