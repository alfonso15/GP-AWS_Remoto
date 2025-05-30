#!/bin/bash

NAME="api.greatplains.comuna18.com"                                  # Name of the application
REPODIR="/srv/backend/api.greatplains.comuna18.com"
NUM_WORKERS=2;                                     # how many worker processes should Gunicorn spawn

DJANGODIR="$REPODIR/src"        # Django project directory
SOCKFILE="$REPODIR/run/gunicorn.sock"  # we will communicte using this unix socket
USER=backend	# the user to run as
GROUP=backend	# the group to run as
DJANGO_SETTINGS_MODULE=app.settings
DJANGO_WSGI_MODULE=app.wsgi                     # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source ../tmp/venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ../tmp/venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application   --name $NAME   --workers $NUM_WORKERS   --user=$USER --group=$GROUP   --bind=unix:$SOCKFILE   --log-level=debug   --log-file=-
