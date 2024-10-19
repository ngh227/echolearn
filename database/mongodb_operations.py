# app/database/mongodb_operations.py
import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from pymongo.errors import ConnectionFailure

load_dotenv()

class MongoDBOperations:
    def __init__(self):
        self.MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
        self.client = MongoClient(self.MONGODB_CONNECTION_STRING)
        self.db = self.client['echolearn']
        self.documents = self.db['documents']
        self.user_responses = self.db['user_responses']
        self.evaluations = self.db['evaluations']

    def test_connection(self):
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            return True
        except ConnectionFailure as e:
            print(f"Connection to MongoDB failed: {e}")
            return False

    def insert_document(self, title, s3_url, user_id, content):
        return self.documents.insert_one({
            "title": title,
            "s3_url": s3_url,
            "user_id": user_id,
            "content": content,
            "upload_date": datetime.utcnow()
        }).inserted_id

    def get_all_documents(self):
        return list(self.documents.find())

    def get_document_by_id(self, document_id):
        return self.documents.find_one({"_id": document_id})

    def insert_user_response(self, document_id, question_id, user_id, response):
        return self.user_responses.insert_one({
            "document_id": document_id,
            "question_id": question_id,
            "user_id": user_id,
            "response": response,
            "timestamp": datetime.utcnow()
        }).inserted_id

    def insert_evaluation(self, response_id, score):
        return self.evaluations.insert_one({
            "response_id": response_id,
            "score": score,
            "timestamp": datetime.utcnow()
        }).inserted_id

# Instantiate the MongoDBOperations class
mongodb_ops = MongoDBOperations()

# Test the connection when the module is imported
if mongodb_ops.test_connection():
    print("MongoDB connection test passed.")
else:
    print("MongoDB connection test failed.")