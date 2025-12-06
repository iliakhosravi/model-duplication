from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# from .llm_utils import ask_evaluator
from .models import EvaluationLog

# Create your views here.
@csrf_exempt
def evaluator_view(request):
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			info = data.get("info", "")
			question = data.get("question", "")
			userid = data.get("userid", "")
			result = ''
			# result = ask_evaluator(info, question)
			# Save to MongoDB
			EvaluationLog(
				userid=userid,
				info=info,
				question=question,
				response=result
			).save()
			return JsonResponse({"result": result})
		except Exception as e:
			return JsonResponse({"error": str(e)}, status=400)
	else:
		return JsonResponse({"error": "Only POST allowed."}, status=405)
