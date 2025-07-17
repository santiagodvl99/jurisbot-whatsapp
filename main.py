from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Conteo de preguntas por número (memoria simple)
users = {}

# Prompt base de tu bot legal
SYSTEM_PROMPT = """Eres un asistente virtual experto en jurisprudencia colombiana.
Respondes con precisión, usando lenguaje legal claro, sin emitir opiniones personales.
Siempre citas las normas y/o sentencias relevantes si aplica."""

# Ruta de prueba
@app.route('/')
def home():
    return "¡Bot legal activo!"

# Ruta para recibir mensajes desde Twilio
@app.route('/webhook', methods=['POST'])
def webhook():
    sender = request.form.get('From')  # Número del usuario
    message = request.form.get('Body')  # Mensaje enviado

    # Normaliza el número
    sender = sender.replace("whatsapp:", "")

    # Inicializa o aumenta contador
    if sender not in users:
        users[sender] = 1
    else:
        users[sender] += 1

    # Límite gratuito: 3 preguntas
    if users[sender] > 3:
        reply = "Has usado tus 3 preguntas gratuitas. Para seguir usando el asistente legal, suscríbete escribiendo: *QUIERO SUSCRIBIRME*."
    else:
        # Consulta a OpenAI
        reply = get_gpt_response(message)

    return respond_whatsapp(reply)

def respond_whatsapp(message):
    return f"""<Response>
    <Message>{message}</Message>
    </Response>"""

def get_gpt_response(user_input):
    api_key = os.environ.get("OPENAI_API_KEY")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result['choices'][0]['message']['content']

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
