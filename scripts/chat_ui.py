#!/usr/bin/env python3
"""
Gradio Chat UI for Fine-Tuned Book Expert
Supports Spanish/English with content guardrails.
"""

import gradio as gr
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

SYSTEM_PROMPT_ES = """Eres un asistente útil que responde preguntas sobre el libro
'El gran libro de Lucía, mi pediatra' de Lucía Galán Bertrand.
Responde siempre en español de forma clara y concisa.
Si no tienes información sobre algo, dilo honestamente."""

SYSTEM_PROMPT_EN = """You are a helpful assistant that answers questions about the book
'El gran libro de Lucía, mi pediatrician' by Lucía Galán Bertrand.
Respond in English clearly and concisely.
If you don't have information about something, say so honestly."""


def respond(message, history, language):
    """Generate response with guardrails."""
    is_blocked, msg = input_guardrail.check(message)
    if is_blocked:
        return msg

    system_prompt = SYSTEM_PROMPT_ES if language == "Español" else SYSTEM_PROMPT_EN
    prompt = f"{system_prompt}\n\nPregunta: {message}\n\nRespuesta:"

    try:
        response = generate(
            MODEL,
            ADAPTER_PATH,
            prompt=prompt,
            max_tokens=MAX_TOKENS
        )
        is_blocked, safe_response = output_guardrail.check(response)
        return safe_response if is_blocked else response
    except Exception as e:
        return f"Error: {str(e)}"


def create_app():
    """Create and configure Gradio app."""
    with gr.Blocks(title="Chat del Libro") as app:
        gr.Markdown("# 📚 Chat con el Libro")
        gr.Markdown("Pregunta sobre *El gran libro de Lucía, mi pediatra*")

        with gr.Row():
            language = gr.Radio(
                ["Español", "English"],
                value="Español",
                label="Idioma / Language"
            )

        chatbot = gr.Chatbot(
            label="Conversación",
            placeholder="Escribe tu pregunta aquí..."
        )

        msg = gr.Textbox(
            label="Tu pregunta",
            placeholder="¿Qué quieres saber sobre el libro?",
            lines=2
        )

        with gr.Row():
            submit = gr.Button("Enviar", variant="primary")
            clear = gr.Button("Limpiar chat")

        submit.click(fn=respond, inputs=[msg, chatbot, language], outputs=[chatbot])
        msg.submit(fn=respond, inputs=[msg, chatbot, language], outputs=[chatbot])
        clear.click(lambda: (None, ""), outputs=[chatbot, msg])

    return app


def main():
    """Launch the app."""
    app = create_app()
    print("\n🚀 Starting Chat UI...")
    print("📖 URL: http://localhost:7860")
    print("🔗 Share link will be generated automatically\n")

    app.launch(share=True, server_name="0.0.0.0")


if __name__ == "__main__":
    main()