import os
from urllib.parse import urlparse
from s3_service import S3Service
from pdf_processor import PDFProcessor
from embedder import JinaAIEmbedder
import google.generativeai as genai
import numpy as np
from datetime import datetime

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from pymongo.errors import ConnectionFailure
from bson import ObjectId
import uuid
from urllib.parse import urlparse
import unittest

class MongoDBOperations:
    def __init__(self):
        load_dotenv()
        self.MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
        self.client = MongoClient(self.MONGODB_CONNECTION_STRING)
        self.db = self.client['echolearn']
        self.documents = self.db['documents']
        self.user_responses = self.db['user_responses']
        self.evaluations = self.db['evaluations']
        self.embeddings = self.db['embeddings']
        self.chat_history = self.db['chat_history']

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
    def get_document_by_id(self, doc_id):
        """Retrieve a document by its MongoDB ObjectID."""
        try:
            document = self.collection.find_one({"_id": ObjectId(doc_id)})
            return document
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None
    def insert_evaluation(self, user_id, document_id, score):
        return self.evaluations.insert_one({
            "user_id": user_id,
            "document_id": document_id,
            "score": score,
            "timestamp": datetime.utcnow()
        }).inserted_id

    def insert_or_update_embedding(self, document_id, embeddings, text):
        return self.embeddings.update_one(
            {"document_id": ObjectId(document_id)},
            {"$set": {
                "embeddings": embeddings,
                "text": text,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        ).upserted_id

    def get_embedding(self, document_id):
        return self.embeddings.find_one({"document_id": ObjectId(document_id)})
    
    def get_document_content(self, doc_id):
        """
        Retrieve the content of a document by its MongoDB ObjectID.
        """
        try:
            document = self.documents.find_one({"_id": ObjectId(doc_id)})
            if document:
                return document.get("content", "")  # Assuming the content is stored in a 'content' field
            else:
                return ""
        except Exception as e:
            print(f"Error retrieving document content: {e}")
            return ""
    
    def insert_chat_history(self, chat_entry):
        return self.chat_history.insert_one(chat_entry).inserted_id

    def get_chat_history(self, doc_id):
        return list(self.chat_history.find({"document_id": ObjectId(doc_id)}).sort("timestamp", 1))
    
    def close_connection(self):
        self.client.close()


class PDFProcessingWorkflow:
    def __init__(self):
        self.s3_service = S3Service()
        self.pdf_processor = PDFProcessor()
        self.embedder = JinaAIEmbedder()
        self.mongo_ops = MongoDBOperations()
        
        # Configure Gemini AI
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-pro")
        
    def upload_file(self, file_path):
        """
        Upload a file to S3 and return the S3 URI.
        """
        file_name = os.path.basename(file_path)
        object_name = f"uploads/{str(uuid.uuid4())}-{file_name}"
        bucket_name = os.getenv("S3_BUCKET_NAME")

        if self.s3_service.upload_file(file_path, object_name):
            return f"s3://{bucket_name}/{object_name}"
        else:
            raise Exception("Failed to upload file to S3")
        
    def process_pdf(self, s3_uri):
        # Parse the S3 URI
        parsed_uri = urlparse(s3_uri)
        bucket_name = parsed_uri.netloc
        object_key = parsed_uri.path.lstrip('/')

        # Download PDF from S3
        local_path = f"/tmp/{os.path.basename(object_key)}"
        self.s3_service.download_file(bucket_name, object_key, local_path)

        # Extract text from PDF
        pdf_text = self.pdf_processor.extract_text(local_path)

        # Generate embedding for the PDF text
        embedding = self.embedder.generate_embedding(pdf_text)

        # Save text and embedding to MongoDB
        doc_id = self.mongo_ops.insert_document(s3_uri, pdf_text)
        self.mongo_ops.insert_or_update_embedding(doc_id, embedding, pdf_text)

        # Generate questions using Gemini AI
        questions = self.generate_questions(pdf_text, doc_id)

        # Clean up local file
        os.remove(local_path)

        return doc_id, questions
    
    def run_workflow(self, file_path):
        try:
            # Step 1: Upload file to S3
            s3_uri = self.upload_file(file_path)
            print(f"File uploaded successfully. S3 URI: {s3_uri}")

            # Step 2: Process the PDF
            doc_id, questions = self.process_pdf(s3_uri)
            print(f"Document processed. ID: {doc_id}")
            print("Generated questions:")
            for i, question in enumerate(questions, 1):
                print(f"{i}. {question}")

            return doc_id, questions, s3_uri
        except Exception as e:
            print(f"An error occurred during the workflow: {e}")
            return None, [], None


    def generate_questions(self, text, doc_id):
        prompt = f"Based on the following text, generate 5 questions to test the reader's understanding:\n\n{text[:4000]}"
        response = self.model.generate_content(prompt)
        questions = response.text.strip().split('\n')
        
        # Save the generated questions to chat history
        self.save_chat_history(doc_id, "system", questions)
        
        return questions

    def evaluate_answer(self, doc_id, user_answer):
        # Retrieve original document embedding
        doc_embedding = self.mongo_ops.get_embedding(doc_id)

        # Generate embedding for user's answer
        answer_embedding = self.embedder.generate_embedding(user_answer)

        # Compare embeddings using cosine similarity
        similarity = np.dot(doc_embedding['embeddings'], answer_embedding) / (
            np.linalg.norm(doc_embedding['embeddings']) * np.linalg.norm(answer_embedding)
        )

        # Convert similarity to a percentage score
        score = int(similarity * 100)

        return score

    def save_chat_history(self, doc_id, role, content):
        chat_entry = {
            "document_id": doc_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        self.mongo_ops.insert_chat_history(chat_entry)

    def get_chat_history(self, doc_id):
        return self.mongo_ops.get_chat_history(doc_id)

    def upload_file_from_chat(self, file_content, file_name):
        """
        Upload a file to S3 from chat and return the S3 URI.
        """
        # Generate a unique object name
        object_name = f"uploads/{str(uuid.uuid4())}-{file_name}"
        bucket_name = os.getenv("S3_BUCKET_NAME")

        # Save the file content temporarily
        temp_path = f"/tmp/{file_name}"
        with open(temp_path, 'wb') as f:
            f.write(file_content)

        # Upload to S3
        if self.s3_service.upload_file(temp_path, object_name):
            # Clean up the temporary file
            os.remove(temp_path)
            return f"s3://{bucket_name}/{object_name}"
        else:
            # Clean up the temporary file
            os.remove(temp_path)
            raise Exception("Failed to upload file to S3")
        
    def chat_based_workflow(self, file_content, file_name):
        try:
            # Step 1: Upload file to S3
            s3_uri = self.upload_file_from_chat(file_content, file_name)
            print(f"File uploaded successfully. S3 URI: {s3_uri}")

            # Step 2: Process the PDF
            doc_id, questions = self.process_pdf(s3_uri)
            print(f"Document processed. ID: {doc_id}")
            print("Generated questions:")
            for i, question in enumerate(questions, 1):
                print(f"{i}. {question}")

            return doc_id, questions, s3_uri
        except Exception as e:
            print(f"An error occurred during the workflow: {e}")
            return None, [], None

    def generate_more_questions(self, doc_id):
        chat_history = self.get_chat_history(doc_id)
        
        # Construct a prompt that includes previous questions and answers
        prompt = "Based on the following chat history and document content, generate 5 new questions to further test the reader's understanding:\n\n"
        for entry in chat_history:
            prompt += f"{entry['role'].capitalize()}: {entry['content']}\n"
        
        # Add the document content (you might want to limit this if it's too long)
        doc_content = self.mongo_ops.get_document_content(doc_id)
        prompt += f"\nDocument content: {doc_content[:2000]}..."  # Limiting to 2000 chars as an example
        
        response = self.model.generate_content(prompt)
        new_questions = response.text.strip().split('\n')
        
        # Save the new questions to chat history
        self.save_chat_history(doc_id, "system", new_questions)
        
        return new_questions

    def run_workflow(self, s3_uri):
        doc_id, questions = self.process_pdf(s3_uri)
        print(f"Document processed. ID: {doc_id}")
        print("Generated questions:")
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")

        while True:
            user_answer = input("Please provide your answer to one of the questions (or type 'more' for more questions, 'quit' to exit): ")
            if user_answer.lower() == 'quit':
                break
            elif user_answer.lower() == 'more':
                new_questions = self.generate_more_questions(doc_id)
                print("Additional questions:")
                for i, question in enumerate(new_questions, 1):
                    print(f"{i}. {question}")
            else:
                self.save_chat_history(doc_id, "user", user_answer)
                score = self.evaluate_answer(doc_id, user_answer)
                print(f"Your understanding score: {score}%")

# Usage
if __name__ == "__main__":
    workflow = PDFProcessingWorkflow()
    workflow.run_workflow("s3://echolearn-bucket/ch16.pdf")