#!/usr/bin/env bash
set -o errexit # exit on error

# Ensure execute permissions
chmod +x "$0"

# Change to script directory
cd "$(dirname "$0")"

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
