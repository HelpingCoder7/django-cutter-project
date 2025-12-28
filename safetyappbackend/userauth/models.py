from django.conf import settings

from .dbconnection import db

user_collection = db[settings.MONGO_DB_NAME]
