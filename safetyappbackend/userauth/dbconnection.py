import certifi
from pymongo.mongo_client import MongoClient

mongo_uri = "mongodb+srv://safetyapp:li7CIGUIiBZCJAvT@cluster0.nu2zdsi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
ca = certifi.where()
client = MongoClient(mongo_uri)

db = client["logincollection"]
