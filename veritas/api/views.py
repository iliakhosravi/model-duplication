from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .chat import evaluate_prompt

# Create your views here.
@csrf_exempt
def evaluator_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError as exc:
        return JsonResponse({"error": f"Invalid JSON: {exc}"}, status=400)

    messages = data.get("messages")
    userid = data.get("userid", "anonymous")
    chat_template_params = data.get("chat_template_params") or {}
    tokenizer_input_params = data.get("tokenizer_input_params") or {}
    generation_params = data.get("generation_params") or {}

    if not messages:
        return JsonResponse({"error": "messages are required"}, status=400)

    try:
        result = evaluate_prompt(
            messages=messages,
            userid=userid,
            chat_template_params=chat_template_params,
            tokenizer_input_params=tokenizer_input_params,
            generation_params=generation_params,
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({
        "answer": result,
        "messages": messages,
        "userid": userid,
        "chat_template_params": chat_template_params,
        "tokenizer_input_params": tokenizer_input_params,
        "generation_params": generation_params,
    })


def health_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed."}, status=405)

    return JsonResponse({"status": "ok"})
