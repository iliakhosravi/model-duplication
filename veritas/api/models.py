
from mongoengine import Document, StringField, DateTimeField, DictField
import datetime


class EvaluationLog(Document):
    userid = StringField(required=True)
    parameters = DictField(required=True)  # Persist parameters that shape the model call
    response = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
