import certifi
from django.conf import settings
from pymongo.mongo_client import MongoClient

ca = certifi.where()
client = MongoClient(settings.MONGO_URI, tlsCAFile=ca)

db = client[settings.MONGO_COLLECTION_NAME]
