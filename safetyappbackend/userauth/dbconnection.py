import certifi
from pymongo.mongo_client import MongoClient
from django.conf import settings

# mongo_uri = "mongodb+srv://safetyapp:li7CIGUIiBZCJAvT@cluster0.nu2zdsi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

ca = certifi.where()
client = MongoClient(settings.MONGO_URI, tlsCAFile=ca)

db = client[settings.MONGO_COLLECTION_NAME]
