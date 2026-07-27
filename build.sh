#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python core/manage.py collectstatic --no-input
python core/manage.py migrate
