import os 
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from pymongo.errors import ConnectionFailure
import unittest

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

SAMPLE_TITLE = "Test Document"
SAMPLE_S3_URL = "https://example.com/test-document"

class TestMongoDBConnection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a temporary collection for testing."""
        cls.client = client
        cls.db = db
        cls.documents = documents

    def test_connection(self):
        """Test if the connection to MongoDB is successful."""
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except ConnectionFailure as e:
            self.fail(f"Connection to MongoDB failed: {e}")

    def test_insert_document(self):
        """Test inserting a document into the 'documents' collection."""
        inserted_id = self.documents.insert_one({
            "title": SAMPLE_TITLE,
            "s3_url": SAMPLE_S3_URL,
            "upload_date": datetime.utcnow()
        }).inserted_id
        self.assertIsNotNone(inserted_id)
        
        # Check if the document is actually in the collection
        document = self.documents.find_one({"_id": inserted_id})
        self.assertIsNotNone(document)
        self.assertEqual(document['title'], SAMPLE_TITLE)
        self.assertEqual(document['s3_url'], SAMPLE_S3_URL)

    def test_get_all_documents(self):
        """Test retrieving all documents from the 'documents' collection."""
        all_documents = list(self.documents.find())
        self.assertIsInstance(all_documents, list)

    @classmethod
    def tearDownClass(cls):
        """Clean up test data from the collection."""
        cls.documents.delete_many({"title": SAMPLE_TITLE})
        print("Cleaned up test data.")

if __name__ == '__main__':
    unittest.main()