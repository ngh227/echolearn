# app/services/speech_to_text_service.py

import boto3
from botocore.exceptions import ClientError
import time
import logging
import os

class SpeechToTextService:
    def __init__(self, region_name='us-east-1'):
        self.transcribe = boto3.client('transcribe', region_name=region_name)
        self.s3 = boto3.client('s3', region_name=region_name)
        self.logger = logging.getLogger(__name__)
        self.bucket_name = 'echolearn-bucket'  # existing bucket
    def transcribe_audio_file(self, file_path, language_code='en-US'):
        try:
            # Generate a unique job name
            job_name = f"transcription_job_{int(time.time())}"
            
            # Upload the file to S3 temporarily
            s3_key = f"temp_audio/{os.path.basename(file_path)}"
            self.s3.upload_file(file_path, self.bucket_name, s3_key)
            
            # Start the transcription job
            response = self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f"s3://{self.bucket_name}/{s3_key}"},
                MediaFormat=file_path.split('.')[-1],  # Assumes file extension is the format
                LanguageCode=language_code
            )
            
            self.logger.info(f"Transcription job {job_name} started successfully.")
            
            # Wait for the job to complete
            transcript_text = self.get_transcription_result(job_name)
            
            # Clean up: delete the temporary file from S3
            self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            
            return transcript_text
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio file: {e}")
            return None

    def get_transcription_result(self, job_name, wait_time=5, max_tries=60):
        tries = 0
        while tries < max_tries:
            tries += 1
            try:
                result = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
                status = result['TranscriptionJob']['TranscriptionJobStatus']
                
                if status == 'COMPLETED':
                    transcript_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    self.logger.info(f"Transcription job {job_name} completed successfully.")
                    
                    # Download the transcript file
                    transcript_response = self.s3.get_object(Bucket=self.bucket_name, Key=transcript_uri.split('/')[-1])
                    transcript_data = transcript_response['Body'].read().decode('utf-8')
                    
                    # Parse the JSON to get the transcript text
                    import json
                    transcript_text = json.loads(transcript_data)['results']['transcripts'][0]['transcript']
                    
                    return transcript_text

                elif status == 'FAILED':
                    self.logger.error(f"Transcription job {job_name} failed.")
                    return None

                self.logger.info(f"Waiting for transcription job {job_name} to complete. Attempt {tries}/{max_tries}.")
                time.sleep(wait_time)
            except ClientError as e:
                self.logger.error(f"Error checking transcription job status: {e}")
                return None

        self.logger.error(f"Transcription job {job_name} did not complete within the allowed attempts.")
        return None

# Usage example:
# stt_service = SpeechToTextService()
# transcript = stt_service.transcribe_audio_file('path/to/your/audio/file.webm')
# print(transcript)