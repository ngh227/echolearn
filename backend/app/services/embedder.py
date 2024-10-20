import os
import requests
from dotenv import load_dotenv
import tiktoken

class JinaAIEmbedder:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('JINAAI_API_KEY')
        if not self.api_key:
            raise ValueError("JINAAI_API_KEY not found in environment variables")
        
        self.api_url = 'https://api.jina.ai/v1/embeddings'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.model = 'jina-embeddings-v2-base-en'
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.max_tokens = 8000  # Setting slightly below the limit for safety

    def generate_embedding(self, text: str):
        if not text:
            raise ValueError("Input text cannot be empty")

        # Tokenize the text
        tokens = self.tokenizer.encode(text)

        # If the text is too long, we'll need to split it
        if len(tokens) > self.max_tokens:
            print(f"Text is too long ({len(tokens)} tokens). Splitting into chunks.")
            chunks = self.split_into_chunks(tokens)
            embeddings = []
            for chunk in chunks:
                chunk_text = self.tokenizer.decode(chunk)
                embedding = self._generate_single_embedding(chunk_text)
                if embedding:
                    embeddings.append(embedding)
            # Average the embeddings if we have multiple chunks
            if embeddings:
                return [sum(x) / len(embeddings) for x in zip(*embeddings)]
            else:
                return None
        else:
            return self._generate_single_embedding(text)

    def _generate_single_embedding(self, text: str):
        request_data = {
            'input': [text],
            'model': self.model
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=request_data)
            response.raise_for_status()
            return response.json()['data'][0]['embedding']
        except requests.RequestException as e:
            print(f"Error generating embedding: {str(e)}")
            if response.text:
                print(f"Response content: {response.text}")
            return None

    def split_into_chunks(self, tokens):
        chunks = []
        for i in range(0, len(tokens), self.max_tokens):
            chunks.append(tokens[i:i + self.max_tokens])
        return chunks