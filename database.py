from pymongo import MongoClient
import os

MONGO_CONNECTION_STRING="mongodb+srv://armstrong:armstrong@motley.8aloqo0.mongodb.net/?retryWrites=true&w=majority"

def get_database():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = os.environ.get("MONGO_CONNECTION_STRING", None)
 
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
   client = MongoClient(CONNECTION_STRING)
 
   # Create the database for our example (we will use the same database throughout the tutorial
   return client['motley']
