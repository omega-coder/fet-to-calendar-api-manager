#!/bin/bash

export OAUTHLIB_INSECURE_TRANSPORT=1
export OAUTHLIB_RELAX_TOKEN_SCOPE=1

export FLASK_APP=app.py

echo -e "\e[32m[+] Running app now ...\e[0m"

flask run
















