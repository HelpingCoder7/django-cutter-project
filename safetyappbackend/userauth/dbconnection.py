from pymongo.mongo_client import MongoClient
import certifi
import os



mongo_uri = "mongodb+srv://safetyapp:li7CIGUIiBZCJAvT@cluster0.nu2zdsi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  
# mongo_uri = os.getenv('mongo_uri')
ca = certifi.where()
client = MongoClient(mongo_uri )

db = client['logincollection']
# print("connection done ")

