#!/bin/bash

export OAUTHLIB_INSECURE_TRANSPORT=1
export OAUTHLIB_RELAX_TOKEN_SCOPE=1
export FLASK_RUN_PORT=5000
export FLASK_APP=app.py
export FLASK_DEBUG=1

echo -e "\e[32m[+] Migrating database ...\e[0m"

flask db init
flask db migrate
flask db upgrade


