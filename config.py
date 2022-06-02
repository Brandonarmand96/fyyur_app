import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

#implementation from code reviews
DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
DB_USER = os.getenv('DB_USER', 'leroi')
DB_NAME = os.getenv('DB_NAME', 'fyyur')


# Enable debug mode.
DEBUG = True
WTF_CSRF_ENABLED = False
WTF_CSRF_CHECK_DEFAULT = False
# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://{}@{}/{}'.format(DB_USER, DB_HOST, DB_NAME)
#SQLALCHEMY_DATABASE_URI = 'postgresql://leroi@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
