#!/usr/bin/env python3
"""
Local Inference Endpoint
Serve the fine-tuned model as a local API (like SageMaker real-time endpoint).
"""

import json
import sys
from pathlib import Path
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

sys.path.insert(0, str(Path(__file__).parent))
from guardrails import InputGuardrail, OutputGuardrail


class InferenceHandler(BaseHTTPRequestHandler):
    """HTTP handler for inference requests."""

    model_path = None
    adapter_path = None
    input_guardrail = InputGuardrail()
    output_guardrail = OutputGuardrail()

    def do_POST(self):
        """Handle POST requests."""
        if self.path != '/predict':
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            prompt = data.get('prompt', '')
            max_tokens = data.get('max_tokens', 256)

            filtered_prompt = self.input_guardrail.filter(prompt)

            if "Lo siento" in filtered_prompt:
                response = filtered_prompt
            else:
                response = self._generate(filtered_prompt, max_tokens)

            filtered_response = self.output_guardrail.filter(response)

            result = {
                'response': filtered_response,
                'status': 'success'
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_error(500, str(e))

    def _generate(self, prompt: str, max_tokens: int) -> str:
        """Run model inference."""
        try:
            from mlx_lm import generate
            response = generate(
                self.model_path or "mlx-community/SmolLM2-1.7B-Instruct-4bit",
                self.adapter_path or "./adapters/v1",
                prompt=prompt,
                max_tokens=max_tokens,
            )
            return response
        except Exception as e:
            return f"Error: {e}"

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class ModelServer:
    """Local model server."""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.server = None

    def start(self, model_path: str, adapter_path: str):
        """Start the inference server."""
        InferenceHandler.model_path = model_path
        InferenceHandler.adapter_path = adapter_path

        self.server = HTTPServer((self.host, self.port), InferenceHandler)
        print(f"🚀 Model server started at http://{self.host}:{self.port}")
        print(f"   Endpoint: POST /predict")
        print(f"   Model: {model_path}")
        print(f"   Adapters: {adapter_path}")
        print(f"\n   Example curl:")
        print(f"   curl -X POST http://{self.host}:{self.port}/predict \\")
        print(f"        -H 'Content-Type: application/json' \\")
        print(f"        -d '{{\"prompt\": \"¿Qué es la vida?\", \"max_tokens\": 100}}'")
        print("\nPress Ctrl+C to stop\n")

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            self.stop()

    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            print("✓ Server stopped")


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else None
    adapter = sys.argv[2] if len(sys.argv) > 2 else None
    host = sys.argv[3] if len(sys.argv) > 3 else "localhost"
    port = int(sys.argv[4]) if len(sys.argv) > 4 else 8080

    server = ModelServer(host, port)
    server.start(model, adapter)


if __name__ == "__main__":
    main()