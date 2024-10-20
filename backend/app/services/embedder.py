import os
import requests
from dotenv import load_dotenv

load_dotenv()

class JinaAIEmbedder:
    def __init__(self):
        self.api_key = os.getenv('JINAAI_API_KEY')
        if not self.api_key:
            raise ValueError("JINAAI_API_KEY not found in environment variables")
        
        self.api_url = 'https://api.jina.ai/v1/embeddings'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.model = 'jina-embeddings-v2-base-en' 

    def generate_embedding(self, text: str):
        """
        Generate an embedding for the given text using Jina AI API.
        
        :param text: The input text to generate an embedding for.
        :return: A list representing the embedding vector.
        """
        request_data = {
            'input': [text],
            'model': self.model
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=request_data)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()['data'][0]['embedding']
        except requests.RequestException as e:
            print(f"Error generating embedding: {str(e)}")
            return None

    def generate_embeddings_batch(self, texts: list):
        """
        Generate embeddings for a batch of texts using Jina AI API.
        
        :param texts: A list of input texts to generate embeddings for.
        :return: A list of embedding vectors.
        """
        request_data = {
            'input': texts,
            'model': self.model
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=request_data)
            response.raise_for_status() 
            return [item['embedding'] for item in response.json()['data']]
        except requests.RequestException as e:
            print(f"Error generating embeddings batch: {str(e)}")
            return None