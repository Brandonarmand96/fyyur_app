import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
WTF_CSRF_ENABLED = False
WTF_CSRF_CHECK_DEFAULT = False
# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://leroi@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
