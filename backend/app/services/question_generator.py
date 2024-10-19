from transformers import pipeline

def generate_questions(text):
    question_generator = pipeline("question-generation")
    return question_generator(text)
