from transformers import pipeline

def evaluate_comprehension(question, student_answer, expected_answer):
    nlp = pipeline("text-classification")
    result = nlp(f"Question: {question} \nStudent Answer: {student_answer} \nExpected Answer: {expected_answer}")
    return result
