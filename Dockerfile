FROM ubuntu:16.04

LABEL CHERIEF Yassine "fy_cherief@esi.dz"

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

