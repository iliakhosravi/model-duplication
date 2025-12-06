
from mongoengine import Document, StringField, DateTimeField
import datetime

class EvaluationLog(Document):
	userid = StringField(required=True)
	info = StringField(required=True)
	question = StringField(required=True)
	response = StringField(required=True)
	created_at = DateTimeField(default=datetime.datetime.utcnow)
