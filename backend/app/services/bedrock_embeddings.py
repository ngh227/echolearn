import boto3
import json
from typing import List, Dict
import logging

class BedrockEmbeddingsService:
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        self.logger = logging.getLogger(__name__)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Amazon Titan Text Embeddings v2.

        :param text: The input text to embed
        :return: A list of floats representing the embedding
        """
        try:
            body = json.dumps({"inputText": text})
            response = self.bedrock_runtime.invoke_model(
                modelId="amazon.titan-embed-text-v2:0",
                contentType="application/json",
                accept="application/json",
                body=body
            )
            response_body = json.loads(response.get("body").read())
            embedding = response_body.get("embedding")
            return embedding
        except Exception as e:
            self.logger.error(f"Error generating embedding: {str(e)}")
            return None

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts using Amazon Titan Text Embeddings v2.

        :param texts: A list of input texts to embed
        :return: A list of embeddings, where each embedding is a list of floats
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
        return embeddings

    def segment_and_embed_document(self, document: str, max_tokens: int = 8000) -> List[Dict[str, any]]:
        """
        Segment a long document into chunks and generate embeddings for each chunk.

        :param document: The input document text
        :param max_tokens: Maximum number of tokens per chunk (default: 8000)
        :return: A list of dictionaries containing chunk text and its embedding
        """
        # Simple segmentation by splitting into paragraphs
        paragraphs = document.split('\n\n')
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph

        if current_chunk:
            chunks.append(current_chunk.strip())

        embedded_chunks = []
        for chunk in chunks:
            embedding = self.generate_embedding(chunk)
            if embedding:
                embedded_chunks.append({
                    "text": chunk,
                    "embedding": embedding
                })

        return embedded_chunks

# Example usage
if __name__ == "__main__":
    embedding_service = BedrockEmbeddingsService()

    # Single text embedding
    text = "Hello, world! This is a test."
    embedding = embedding_service.generate_embedding(text)
    print(f"Embedding for '{text}': {embedding[:5]}... (showing first 5 dimensions)")

    # Batch embedding
    texts = ["Hello, world!", "This is another test.", "Embeddings are useful."]
    embeddings = embedding_service.generate_embeddings_batch(texts)
    print(f"Generated {len(embeddings)} embeddings for the batch.")

    # Document segmentation and embedding
    long_document = """
    This is a long document that needs to be segmented.
    It contains multiple paragraphs of text.

    Each paragraph should be embedded separately.
    This allows for better representation of the document's content.

    The BedrockEmbeddingsService will handle the segmentation and embedding.
    """
    embedded_chunks = embedding_service.segment_and_embed_document(long_document)
    print(f"Generated embeddings for {len(embedded_chunks)} chunks of the document.")