import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from pymongo.errors import ConnectionFailure
import unittest
from bson import ObjectId

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
            print("Pinged your deployment. You successfully connected to MongoDB!")
            return True
        except ConnectionFailure as e:
            print(f"Connection to MongoDB failed: {e}")
            return False

    def insert_document(self, title, s3_url):
        return self.documents.insert_one({
            "title": title,
            "s3_url": s3_url,
            "upload_date": datetime.utcnow()
        }).inserted_id

    def get_all_documents(self):
        return list(self.documents.find())

    def insert_user_response(self, user_id, document_id, response):
        return self.user_responses.insert_one({
            "user_id": user_id,
            "document_id": document_id,
            "response": response,
            "timestamp": datetime.utcnow()
        }).inserted_id

    def insert_evaluation(self, user_id, document_id, score):
        return self.evaluations.insert_one({
            "user_id": user_id,
            "document_id": document_id,
            "score": score,
            "timestamp": datetime.utcnow()
        }).inserted_id

    def close_connection(self):
        self.client.close()

class TestMongoDBConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a temporary collection for testing."""
        cls.mongo_ops = MongoDBOperations()
        cls.client = cls.mongo_ops.client
        cls.db = cls.mongo_ops.db
        cls.documents = cls.mongo_ops.documents

    SAMPLE_TITLE = "Test Document"
    SAMPLE_S3_URL = "https://example.com/test-document"

    def test_connection(self):
        """Test if the connection to MongoDB is successful."""
        self.assertTrue(self.mongo_ops.test_connection())

    def test_insert_document(self):
        """Test inserting a document into the 'documents' collection."""
        inserted_id = self.mongo_ops.insert_document(self.SAMPLE_TITLE, self.SAMPLE_S3_URL)
        self.assertIsNotNone(inserted_id)
        
        # Check if the document is actually in the collection
        document = self.documents.find_one({"_id": inserted_id})
        self.assertIsNotNone(document)
        self.assertEqual(document['title'], self.SAMPLE_TITLE)
        self.assertEqual(document['s3_url'], self.SAMPLE_S3_URL)

    def test_get_all_documents(self):
        """Test retrieving all documents from the 'documents' collection."""
        all_documents = self.mongo_ops.get_all_documents()
        self.assertIsInstance(all_documents, list)

    @classmethod
    def tearDownClass(cls):
        """Clean up test data from the collection."""
        cls.documents.delete_many({"title": cls.SAMPLE_TITLE})
        cls.mongo_ops.close_connection()
        print("Cleaned up test data.")

if __name__ == '__main__':
    unittest.main()