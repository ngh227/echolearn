from app.services.speech_to_text_service import SpeechToTextService
import os

def test_transcribe():
    stt_service = SpeechToTextService()
    
    # Path to your test audio file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_audio_file = os.path.join(current_dir, 'app', 'hbd copy.mp3')
    
    try:
        # Transcribe the audio file
        transcript = stt_service.transcribe_audio_file(test_audio_file)
        
        if transcript:
            print(f"Transcription successful. Text: {transcript}")
        else:
            print("Transcription failed or returned no text.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    test_transcribe()