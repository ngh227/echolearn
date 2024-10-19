# app/models.py
from app.database.mongodb_operations import mongodb_ops
from bson import ObjectId

class Document:
    def __init__(self, title, s3_url, user_id, content, _id=None):
        self._id = _id
        self.title = title
        self.s3_url = s3_url
        self.user_id = user_id
        self.content = content

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get('_id'),
            title=data.get('title'),
            s3_url=data.get('s3_url'),
            user_id=data.get('user_id'),
            content=data.get('content')
        )

    def save(self):
        if not self._id:
            result = mongodb_ops.insert_document(self.title, self.s3_url, self.user_id, self.content)
            self._id = result
        else:
            # Update existing document
            mongodb_ops.documents.update_one({"_id": self._id}, {"$set": self.__dict__})
        return self._id

    @staticmethod
    def get_all():
        documents = mongodb_ops.get_all_documents()
        return [Document.from_dict(doc) for doc in documents]

    @staticmethod
    def get_by_id(document_id):
        doc = mongodb_ops.get_document_by_id(ObjectId(document_id))
        return Document.from_dict(doc) if doc else None

class Question:
    def __init__(self, document_id, text, answer, _id=None):
        self._id = _id
        self.document_id = document_id
        self.text = text
        self.answer = answer

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get('_id'),
            document_id=data.get('document_id'),
            text=data.get('text'),
            answer=data.get('answer')
        )

    def save(self):
        if not self._id:
            result = mongodb_ops.insert_question(self.document_id, self.text, self.answer)
            self._id = result
        else:
            # Update existing question
            mongodb_ops.questions.update_one({"_id": self._id}, {"$set": self.__dict__})
        return self._id

    @staticmethod
    def get_by_document_id(document_id):
        questions = mongodb_ops.get_questions_by_document_id(ObjectId(document_id))
        return [Question.from_dict(q) for q in questions]

class UserResponse:
    def __init__(self, document_id, question_id, user_id, response, _id=None):
        self._id = _id
        self.document_id = document_id
        self.question_id = question_id
        self.user_id = user_id
        self.response = response

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get('_id'),
            document_id=data.get('document_id'),
            question_id=data.get('question_id'),
            user_id=data.get('user_id'),
            response=data.get('response')
        )

    def save(self):
        if not self._id:
            result = mongodb_ops.insert_user_response(self.document_id, self.question_id, self.user_id, self.response)
            self._id = result
        else:
            # Update existing response
            mongodb_ops.user_responses.update_one({"_id": self._id}, {"$set": self.__dict__})
        return self._id

class Evaluation:
    def __init__(self, response_id, score, feedback=None, _id=None):
        self._id = _id
        self.response_id = response_id
        self.score = score
        self.feedback = feedback

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get('_id'),
            response_id=data.get('response_id'),
            score=data.get('score'),
            feedback=data.get('feedback')
        )

    def save(self):
        if not self._id:
            result = mongodb_ops.insert_evaluation(self.response_id, self.score, self.feedback)
            self._id = result
        else:
            # Update existing evaluation
            mongodb_ops.evaluations.update_one({"_id": self._id}, {"$set": self.__dict__})
        return self._id

    @staticmethod
    def get_by_response_id(response_id):
        eval_data = mongodb_ops.get_evaluation_by_response_id(ObjectId(response_id))
        return Evaluation.from_dict(eval_data) if eval_data else None