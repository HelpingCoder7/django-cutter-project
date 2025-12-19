from .dbconnection import db
from django.conf import settings
user_collection = db[settings.MONGO_DB_NAME]
