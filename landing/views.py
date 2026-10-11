import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .chat import answer
from .copy import COPY, normalise_lang

LANG_COOKIE = "aplicamosia_lang"


def resolve_lang(request):
    chosen = normalise_lang(request.GET.get("lang"))
    if chosen:
        return chosen
    return normalise_lang(request.COOKIES.get(LANG_COOKIE)) or "es"


def home(request):
    lang = resolve_lang(request)
    copy = COPY[lang]
    chat_i18n = json.dumps(
        {
            "lang": lang,
            "subject": copy["mail_subject"],
            "email": copy["mail_body_email"],
            "company": copy["mail_body_company"],
            "chat": copy["mail_body_chat"],
            "fallback": [copy["fallback_1"], copy["fallback_2"], copy["fallback_3"]],
            "more": copy["fallback_more"],
        },
        ensure_ascii=False,
    )
    response = render(
        request,
        "landing/home.html",
        {"lang": lang, "c": copy, "chat_i18n": chat_i18n},
    )
    if normalise_lang(request.GET.get("lang")):
        response.set_cookie(LANG_COOKIE, lang, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return response


@csrf_exempt
@require_POST
def chat(request):
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"reply": "No he podido leer el mensaje.", "ready_for_lead": False}, status=400)

    message = payload.get("message", "")
    history = payload.get("history") or []
    lang = payload.get("lang") if payload.get("lang") in {"es", "en"} else "es"
    empty = "Escribe qué necesitas." if lang == "es" else "Tell me what you need."
    if not isinstance(message, str) or not message.strip():
        return JsonResponse({"reply": empty, "ready_for_lead": False}, status=400)
    if not isinstance(history, list):
        history = []

    return JsonResponse(answer(message.strip(), history, lang=lang))
