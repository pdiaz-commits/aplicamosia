import json
import os
import urllib.error
import urllib.request

READY_TAG = "[LISTO_PARA_ENVIO]"

SYSTEM_PROMPT_EN = """You are the sales assistant for AplicamosIA, an AI agency. Write in British English.

Rules:
- Talk only about AplicamosIA: systems that sell, support customers and automate work.
- Do not invent clients, logos, prices or fixed deadlines. The pilot is described as a guide of 7 days.
- 120 words maximum. One or two questions per turn.
- Flow: 1) what the business does, 2) which process hurts, 3) which tools they use, 4) propose Diagnostic, 7-day pilot or System in operation.
- When you have sector + process + an idea of how to help, offer to email the summary and add exactly [LISTO_PARA_ENVIO] on its own line.
- If they ask about another brand or unrelated topics, bring the conversation back to AplicamosIA.
- Contact: merlin655040999@gmail.com
"""

SYSTEM_PROMPT = """Eres el asistente comercial de AplicamosIA, una agencia de IA.

Reglas:
- Habla solo de AplicamosIA: sistemas que venden, atienden y automatizan.
- No inventes clientes, logos, precios ni plazos cerrados. El piloto se presenta como 7 días orientativos.
- Máximo 120 palabras. Una o dos preguntas por turno.
- Flujo: 1) qué hace el negocio, 2) qué proceso duele, 3) qué herramientas usan, 4) propone Diagnóstico, Piloto en 7 días o Sistema en marcha.
- Cuando tengas sector + proceso + una idea de ayuda, ofrece enviar el resumen por correo y añade exactamente [LISTO_PARA_ENVIO] en una línea sola.
- Si preguntan por otra marca o temas ajenos, redirige a AplicamosIA.
- Contacto: merlin655040999@gmail.com
"""


def _user_turns(history, message):
    count = 1
    for item in history or []:
        if item.get("role") == "user":
            count += 1
    if message:
        pass
    return count


def guided_reply(message, history, lang="es"):
    text = (message or "").strip()
    turns = _user_turns(history, text)
    low = text.lower()

    if lang == "en":
        if turns <= 1:
            return (
                "Thank you. To narrow the case: does your company sell, support customers, "
                "or carry a lot of repetitive work in operations?"
            ), False
        if turns == 2:
            return (
                "Understood. What tool do you use for that today (WhatsApp, a CRM, email, "
                "a spreadsheet or something else), and where does it get stuck: slow replies, "
                "follow-up or manual tasks?"
            ), False
        if any(word in low for word in ("price", "cost", "how much", "quote", "fee")):
            return (
                "I do not close prices in chat. The usual path is a diagnostic and, "
                "if it fits, a visible pilot in 7 days. Shall I email you a summary "
                "so you can request that diagnostic?"
            ), True
        return (
            "From what you describe, a bounded pilot fits: an agent or an automation "
            "on that flow, with a human in control. The first step is a diagnostic. "
            "Shall we email this summary so we can continue?"
        ), True

    if turns <= 1:
        return (
            "Gracias. Para acotar el caso: ¿tu empresa vende, atiende clientes "
            "o arrastra mucho trabajo repetitivo en operaciones?"
        ), False

    if turns == 2:
        return (
            "Entendido. ¿Qué herramienta usáis hoy para eso (WhatsApp, CRM, correo, "
            "Excel u otra) y qué se atasca: respuesta lenta, seguimiento o tareas a mano?"
        ), False

    if any(word in low for word in ("precio", "cuánto", "cuanto", "coste", "tarifa")):
        return (
            "No cierro precios por chat. El camino habitual es un diagnóstico y, "
            "si encaja, un piloto visible en 7 días. ¿Quieres que te envíe un resumen "
            "para pedir ese diagnóstico?"
        ), True

    reply = (
        "Con lo que cuentas encaja un piloto acotado: un agente o una automatización "
        "sobre ese flujo, con control humano. El primer paso es un diagnóstico. "
        "¿Quieres que enviemos este resumen por correo para continuar?"
    )
    return reply, True


def groq_reply(message, history, lang="es"):
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        return None

    prompt = SYSTEM_PROMPT_EN if lang == "en" else SYSTEM_PROMPT
    messages = [{"role": "system", "content": prompt}]
    for item in (history or [])[-10:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content[:4000]})
    messages.append({"role": "user", "content": (message or "")[:2000]})

    payload = json.dumps(
        {
            "model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
            "messages": messages,
            "temperature": 0.45,
            "max_tokens": 512,
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return None

    reply = (
        (data.get("choices") or [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    if not reply:
        return None
    ready = READY_TAG in reply
    return reply.replace(READY_TAG, "").strip(), ready


def answer(message, history, lang="es"):
    remote = groq_reply(message, history, lang=lang)
    if remote:
        return {"reply": remote[0], "ready_for_lead": remote[1], "engine": "groq"}
    reply, ready = guided_reply(message, history, lang=lang)
    return {"reply": reply, "ready_for_lead": ready, "engine": "guided"}
