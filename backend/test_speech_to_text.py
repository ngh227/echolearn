# backend/test_speech_to_text.py
from app.services.speech_to_text_service import SpeechToTextService
from app.services.s3_service import S3Service
import uuid

def test_speech_to_text():
    # Initialize services
    s3_service = S3Service()
    stt_service = SpeechToTextService()
    
    # Step 1: Upload a test audio file to S3
    test_audio_file_path = "hbd_copy.mp3"  # Change this to your actual test audio file path
    unique_filename = f"{uuid.uuid4()}_{test_audio_file_path}"
    
    # Upload to S3
    s3_url = s3_service.upload_file(test_audio_file_path, unique_filename)
    if not s3_url:
        print("Failed to upload audio file to S3.")
        return
    
    print(f"Audio file uploaded successfully to S3 at: {s3_url}")

    # Step 2: Start the transcription job
    job_name = f"test_transcription_job_{uuid.uuid4()}"
    transcription_response = stt_service.start_transcription_job(s3_url, job_name)
    if not transcription_response:
        print("Failed to start transcription job.")
        return

    print(f"Transcription job started successfully with job name: {job_name}")

    # Step 3: Fetch the transcription result
    transcript_text = stt_service.get_transcription_result(job_name)
    if not transcript_text:
        print("Failed to fetch transcription result.")
    else:
        print(f"Transcription result: {transcript_text}")

if __name__ == "__main__":
    test_speech_to_text()
