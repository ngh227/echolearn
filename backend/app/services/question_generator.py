# app/services/question_generator.py
from transformers import T5ForConditionalGeneration, T5Tokenizer

class QuestionGenerator:
    def __init__(self):
        self.model = T5ForConditionalGeneration.from_pretrained('t5-small')
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')

    def generate_questions(self, context, num_questions=5):
        input_text = f"generate questions: {context}"
        inputs = self.tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True)
        
        outputs = self.model.generate(inputs, max_length=64, num_return_sequences=num_questions, num_beams=4, early_stopping=True)
        
        questions = [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
        return questions
    