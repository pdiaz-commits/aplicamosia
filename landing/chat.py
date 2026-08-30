import json
import os
import urllib.error
import urllib.request

READY_TAG = "[LISTO_PARA_ENVIO]"

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


def guided_reply(message, history):
    text = (message or "").strip()
    turns = _user_turns(history, text)
    low = text.lower()

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


def groq_reply(message, history):
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        return None

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
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


def answer(message, history):
    remote = groq_reply(message, history)
    if remote:
        return {"reply": remote[0], "ready_for_lead": remote[1], "engine": "groq"}
    reply, ready = guided_reply(message, history)
    return {"reply": reply, "ready_for_lead": ready, "engine": "guided"}
