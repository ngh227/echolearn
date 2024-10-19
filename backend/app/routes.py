from flask import Blueprint, request, jsonify
from .services.s3_service import upload_file_to_s3
from .services.pdf_processor import extract_text_from_pdf
from .services.question_generator import generate_questions
from .services.comprehension_evaluator import evaluate_comprehension

routes = Blueprint('routes', __name__)

@routes.route('/upload', methods=['POST'])
def upload_pdf():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    filename = file.filename
    s3_url = upload_file_to_s3(file, filename)
    if not s3_url:
        return jsonify({"error": "Failed to upload to S3"}), 500

    extracted_text = extract_text_from_pdf(file)
    return jsonify({"url": s3_url, "text": extracted_text}), 200

@routes.route('/generate-questions', methods=['POST'])
def generate_questions_route():
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    questions = generate_questions(text)
    return jsonify({"questions": questions}), 200

@routes.route('/evaluate-answer', methods=['POST'])
def evaluate_answer():
    data = request.get_json()
    question = data.get("question")
    student_answer = data.get("student_answer")
    expected_answer = data.get("expected_answer")

    if not question or not student_answer or not expected_answer:
        return jsonify({"error": "Missing data"}), 400

    result = evaluate_comprehension(question, student_answer, expected_answer)
    return jsonify(result), 200
