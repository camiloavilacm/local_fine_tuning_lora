#!/usr/bin/env python3
"""
Simple Flask-based Chat UI for Fine-Tuned Book Expert
More stable than Gradio for local use.
"""

import os
from flask import Flask, render_template_string, request, jsonify
from mlx_lm import generate
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from guardrails import InputGuardrail, OutputGuardrail


MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
ADAPTER_PATH = "./adapters/v1"
MAX_TOKENS = 256

input_guardrail = InputGuardrail()
output_guardrail = OutputGuardrail()

SYSTEM_PROMPT = """Eres un asistente útil que responde preguntas sobre el libro
'El gran libro de Lucía, mi pediatra' de Lucía Galán Bertrand.
Responde siempre en español de forma clara y concisa."""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat del Libro</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { 
            max-width: 800px; margin: 0 auto; 
            background: white; border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; text-align: center;
        }
        .header h1 { font-size: 2rem; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .chat { height: 400px; overflow-y: auto; padding: 20px; background: #f5f5f5; }
        .message { 
            margin-bottom: 15px; padding: 15px 20px; border-radius: 20px; 
            max-width: 80%; animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .user { background: #667eea; color: white; margin-left: auto; border-bottom-right-radius: 5px; }
        .bot { background: white; color: #333; border: 1px solid #ddd; border-bottom-left-radius: 5px; }
        .input-area { 
            display: flex; gap: 10px; padding: 20px; background: white; 
            border-top: 1px solid #eee;
        }
        input { 
            flex: 1; padding: 15px 20px; border: 2px solid #ddd; 
            border-radius: 50px; font-size: 1rem; outline: none; transition: border-color 0.3s;
        }
        input:focus { border-color: #667eea; }
        button {
            padding: 15px 30px; background: #667eea; color: white;
            border: none; border-radius: 50px; font-size: 1rem; cursor: pointer;
            transition: transform 0.2s, background 0.2s;
        }
        button:hover { transform: scale(1.05); background: #764ba2; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .loading { text-align: center; padding: 20px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Chat con el Libro</h1>
            <p>Pregunta sobre "El gran libro de Lucía, mi pediatra"</p>
        </div>
        <div class="chat" id="chat">
            <div class="message bot">
                ¡Hola! Soy el asistente del libro. Pregúntame cualquier cosa sobre su contenido.
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="prompt" placeholder="Escribe tu pregunta..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()" id="sendBtn">Enviar</button>
        </div>
    </div>
    <script>
        async function sendMessage() {
            const input = document.getElementById('prompt');
            const btn = document.getElementById('sendBtn');
            const chat = document.getElementById('chat');
            const message = input.value.trim();
            if (!message) return;
            
            chat.innerHTML += '<div class="message user">' + message + '</div>';
            chat.innerHTML += '<div class="loading">Escribiendo...</div>';
            chat.scrollTop = chat.scrollHeight;
            input.value = '';
            btn.disabled = true;
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                document.querySelector('.loading').remove();
                chat.innerHTML += '<div class="message bot">' + data.response + '</div>';
            } catch (e) {
                document.querySelector('.loading').remove();
                chat.innerHTML += '<div class="message bot">Error: ' + e.message + '</div>';
            }
            btn.disabled = false;
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

app = Flask(__name__)


@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    is_blocked, response = input_guardrail.check(message)
    if is_blocked:
        return jsonify({"response": response})

    prompt = f"{SYSTEM_PROMPT}\n\nPregunta: {message}\n\nRespuesta:"

    try:
        response = generate(MODEL, ADAPTER_PATH, prompt=prompt, max_tokens=MAX_TOKENS)
        is_blocked, safe_response = output_guardrail.check(response)
        return jsonify({"response": safe_response if is_blocked else response})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})


if __name__ == "__main__":
    print("\n🚀 Starting Chat UI...")
    print("📖 URL: http://localhost:7860\n")
    app.run(host="0.0.0.0", port=7860, debug=False)