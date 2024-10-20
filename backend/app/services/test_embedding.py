import os
import asyncio
import json
import time
import pyaudio
import boto3
import sounddevice
import numpy as np
from datetime import datetime
from urllib.parse import urlparse
import uuid
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from embedder import JinaAIEmbedder
from s3_service import S3Service
from pdf_processor import PDFProcessor
from mongodb_operations import MongoDBOperations

class PDFProcessingWorkflow:
    def __init__(self):
        self.s3_service = S3Service()
        self.pdf_processor = PDFProcessor()
        self.embedder = JinaAIEmbedder()
        self.mongo_ops = MongoDBOperations()
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-pro")
        
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.transcribe_client = TranscribeStreamingClient(region=self.aws_region)

    async def speech_to_text(self):
        stream = await self.transcribe_client.start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=16000,
            media_encoding="pcm",
        )

        async def write_chunks():
            print("\n🎙️ Recording... (Speak now)")
            print("=" * 50)
            start_time = time.time()
            async for chunk, _ in MicStream().mic_stream():
                await stream.input_stream.send_audio_event(audio_chunk=chunk)
                
                # Ensure a minimum recording time of 3 seconds
                if time.time() - start_time > 3 and MicStream.is_silent(chunk):
                    print("\n🛑 Silence detected. Stopping recording...")
                    break
            
            await stream.input_stream.end_stream()
            print("=" * 50)
            print("Recording finished. Processing...")

        handler = TranscriptHandler(stream.output_stream)
        await asyncio.gather(write_chunks(), handler.handle_events())
        
        transcript = handler.get_transcript()
        if not transcript:
            print("No speech detected. Please try again.")
            return await self.speech_to_text()
        return transcript
    
    async def run_workflow(self, s3_uri):
        doc_id, questions = await self.process_pdf(s3_uri)
        print(f"Document processed. ID: {doc_id}")
        print("Generated questions:")
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")

        while True:
            print("\nPlease speak your answer (or say 'more' for more questions, 'quit' to exit)")
            user_answer = await self.speech_to_text()
            print(f"Transcribed answer: {user_answer}")
            
            if 'quit' in user_answer.lower():
                break
            elif 'more' in user_answer.lower():
                new_questions = await self.generate_more_questions(doc_id)
                print("Additional questions:")
                for i, question in enumerate(new_questions, 1):
                    print(f"{i}. {question}")
            else:
                await self.save_chat_history(doc_id, "user", user_answer)
                score = await self.evaluate_answer(doc_id, user_answer)
                print(f"Your understanding score: {score}%")

    async def upload_file(self, file_path):
        file_name = os.path.basename(file_path)
        object_name = f"uploads/{str(uuid.uuid4())}-{file_name}"
        bucket_name = os.getenv("S3_BUCKET_NAME")

        if await asyncio.to_thread(self.s3_service.upload_file, file_path, object_name):
            return f"s3://{bucket_name}/{object_name}"
        else:
            raise Exception("Failed to upload file to S3")

    async def process_pdf(self, s3_uri):
        parsed_uri = urlparse(s3_uri)
        bucket_name = parsed_uri.netloc
        object_key = parsed_uri.path.lstrip('/')

        local_path = f"/tmp/{os.path.basename(object_key)}"
        await asyncio.to_thread(self.s3_service.download_file, bucket_name, object_key, local_path)

        pdf_text = await asyncio.to_thread(self.pdf_processor.extract_text, local_path)
        embedding = await asyncio.to_thread(self.embedder.generate_embedding, pdf_text)

        doc_id = await asyncio.to_thread(self.mongo_ops.insert_document, s3_uri, pdf_text)
        await asyncio.to_thread(self.mongo_ops.insert_or_update_embedding, doc_id, embedding, pdf_text)

        questions = await self.generate_questions(pdf_text, doc_id)

        os.remove(local_path)

        return doc_id, questions

    async def generate_questions(self, text, doc_id):
        prompt = f"Based on the following text, generate 5 questions to test the reader's understanding:\n\n{text[:4000]}"
        response = await asyncio.to_thread(self.model.generate_content, prompt)
        questions = response.text.strip().split('\n')
        
        await self.save_chat_history(doc_id, "system", questions)
        
        return questions

    async def evaluate_answer(self, doc_id, user_answer):
        doc_embedding = await asyncio.to_thread(self.mongo_ops.get_embedding, doc_id)
        answer_embedding = await asyncio.to_thread(self.embedder.generate_embedding, user_answer)

        similarity = np.dot(doc_embedding['embeddings'], answer_embedding) / (
            np.linalg.norm(doc_embedding['embeddings']) * np.linalg.norm(answer_embedding)
        )

        score = int(similarity * 100)
        return score

    async def save_chat_history(self, doc_id, role, content):
        chat_entry = {
            "document_id": doc_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        await asyncio.to_thread(self.mongo_ops.insert_chat_history, chat_entry)

    async def get_chat_history(self, doc_id):
        return await asyncio.to_thread(self.mongo_ops.get_chat_history, doc_id)

    async def generate_more_questions(self, doc_id):
        chat_history = await self.get_chat_history(doc_id)
        
        prompt = "Based on the following chat history and document content, generate 5 new questions to further test the reader's understanding:\n\n"
        for entry in chat_history:
            prompt += f"{entry['role'].capitalize()}: {entry['content']}\n"
        
        doc_content = await asyncio.to_thread(self.mongo_ops.get_document_content, doc_id)
        prompt += f"\nDocument content: {doc_content[:2000]}..."
        
        response = await asyncio.to_thread(self.model.generate_content, prompt)
        new_questions = response.text.strip().split('\n')
        
        await self.save_chat_history(doc_id, "system", new_questions)
        
        return new_questions

class MicStream:
    SILENCE_THRESHOLD = 300  # Lowered threshold for better sensitivity
    SILENCE_DURATION = 10  # Reduced silence duration to 2 seconds

    @staticmethod
    def is_silent(audio_chunk):
        audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(audio_data)))
        return rms < MicStream.SILENCE_THRESHOLD

    async def mic_stream(self):
        loop = asyncio.get_event_loop()
        input_queue = asyncio.Queue()
        silent_chunks = 0
        last_audio_time = time.time()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

        stream = sounddevice.RawInputStream(
            channels=1, samplerate=16000, callback=callback, blocksize=1024, dtype="int16")
        
        with stream:
            while True:
                indata, status = await input_queue.get()
                yield indata, status

                if self.is_silent(indata):
                    silent_chunks += 1
                    if silent_chunks >= (self.SILENCE_DURATION * 16):  # 16 chunks per second
                        if time.time() - last_audio_time > self.SILENCE_DURATION:
                            break
                else:
                    silent_chunks = 0
                    last_audio_time = time.time()


    async def mic_stream(self):
        loop = asyncio.get_event_loop()
        input_queue = asyncio.Queue()
        silent_chunks = 0
        last_audio_time = time.time()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

        stream = sounddevice.RawInputStream(
            channels=1, samplerate=16000, callback=callback, blocksize=1024, dtype="int16")
        
        with stream:
            while True:
                indata, status = await input_queue.get()
                yield indata, status

                if self.is_silent(indata):
                    silent_chunks += 1
                    if silent_chunks >= (self.SILENCE_DURATION * 16):  # 16 chunks per second
                        if time.time() - last_audio_time > self.SILENCE_DURATION:
                            break
                else:
                    silent_chunks = 0
                    last_audio_time = time.time()

class TranscriptHandler(TranscriptResultStreamHandler):
    def __init__(self, stream):
        super().__init__(stream)
        self.transcript = []

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            if not result.is_partial:
                for alt in result.alternatives:
                    self.transcript.append(alt.transcript)

    def get_transcript(self):
        return ' '.join(self.transcript)

if __name__ == "__main__":
    workflow = PDFProcessingWorkflow()
    asyncio.run(workflow.run_workflow("s3://echolearn-bucket/ch16.pdf"))