#!/usr/bin/env bash

set -ex

cd /home/kuma/bots/KumaGPT/caption
# /opt/conda/bin/python3 capsrv.py
/opt/conda/bin/gunicorn -w 1 -b 0.0.0.0:14500 main:app
