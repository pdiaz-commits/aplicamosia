import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .chat import answer


def home(request):
    return render(request, "landing/home.html")


@csrf_exempt
@require_POST
def chat(request):
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"reply": "No he podido leer el mensaje.", "ready_for_lead": False}, status=400)

    message = payload.get("message", "")
    history = payload.get("history") or []
    if not isinstance(message, str) or not message.strip():
        return JsonResponse({"reply": "Escribe qué necesitas.", "ready_for_lead": False}, status=400)
    if not isinstance(history, list):
        history = []

    return JsonResponse(answer(message.strip(), history))
