# app/routes.py
from app import app
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app.services.pdf_processor import PDFProcessor
from app.services.s3_service import S3Service
from app.database.mongodb_operations import mongodb_ops
from app.services.speech_to_text_service import SpeechToTextService
import os
import uuid

s3_service = S3Service()
pdf_processor = PDFProcessor()
stt_service = SpeechToTextService()

ALLOWED_EXTENSIONS = {'pdf', 'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Extract text from PDF
        pdf_text = pdf_processor.extract_text(file)
        if pdf_text is None:
            return jsonify({'error': 'Failed to extract text from PDF'}), 500
        
        # Upload file to S3
        s3_url = s3_service.upload_file(file, filename)
        if not s3_url:
            return jsonify({'error': 'Failed to upload file to S3'}), 500
        
        # Save document metadata to MongoDB
        document_id = mongodb_ops.insert_document(
            title=filename,
            s3_url=s3_url,
            user_id=request.form.get('user_id'),
            content=pdf_text
        )
        
        return jsonify({
            'message': 'File uploaded and processed successfully',
            'document_id': str(document_id)
        }), 200
    return jsonify({'error': 'File upload failed'}), 500

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    # Implementation for question generation
    pass

@app.route('/evaluate_response', methods=['POST'])
def evaluate_response():
    document_id = request.json.get('document_id')
    question_id = request.json.get('question_id')
    user_id = request.json.get('user_id')
    response = request.json.get('response')
    
    # Save user response
    response_id = mongodb_ops.insert_user_response(document_id, question_id, user_id, response)
    
    # Evaluate response (you'll need to implement this logic)
    score = evaluate_user_response(response)  # This function needs to be implemented
    
    # Save evaluation
    evaluation_id = mongodb_ops.insert_evaluation(response_id, score)
    
    return jsonify({
        'message': 'Response evaluated successfully',
        'evaluation_id': str(evaluation_id),
        'score': score
    }), 200

@api.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Save the file temporarily
        temp_filename = f"temp_{uuid.uuid4()}.webm"
        file.save(temp_filename)

        # Transcribe the audio
        stt_service = SpeechToTextService()
        transcript_text = stt_service.transcribe_audio_file(temp_filename)

        if transcript_text is None:
            raise ValueError("Transcription failed")

        # Compare with knowledge base (you need to implement this)
        understanding_score = compare_with_knowledge_base(
            transcript_text, 
            request.form.get('document_id'), 
            request.form.get('question_id')
        )

        # Clean up the temporary file
        os.remove(temp_filename)

        return jsonify({
            'message': 'Audio processed successfully',
            'transcript_text': transcript_text,
            'understanding_score': understanding_score
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500