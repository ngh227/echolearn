import os 
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client['echolearn']
documents = db['documents']
user_responses = db['user_responses']
evaluations = db['evaluations']

# delete later:
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


def insert_document(title, s3_url):
        return documents.insert_one({
        "title": title,
        "s3_url": s3_url,
        "upload_date": datetime.datetime.utcnow()
    }).inserted_id

def get_all_documents():
    return list(documents.find())



