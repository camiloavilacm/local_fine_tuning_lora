"""
Input Guardrail - Filter user prompts before model inference
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from .blocklist import Blocklist


class InputGuardrail:
    """Filter input prompts for safety."""

    DEFAULT_RESPONSE = "Lo siento, no puedo ayudarte con esa solicitud. ¿Hay algo más en lo que pueda ayudarte?"

    RESPONSES = {
        'violence': "No puedo ayudarte con contenido violento.",
        'hate': "No puedo ayudarte con contenido de odio.",
        'self_harm': "Si estás pensando en hacerte daño, por favor busca ayuda profesional. Línea de ayuda: 024 (España)",
        'sexual': "No puedo generar ese contenido.",
        'illegal': "No puedo ayudarte con actividades ilegales.",
    }

    def __init__(self, log_path: str = "logs/guardrails_input.log"):
        self.blocklist = Blocklist()
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging."""
        self.logger = logging.getLogger('input_guardrail')
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.log_path)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)

    def check(self, prompt: str) -> tuple[bool, Optional[str]]:
        """
        Check if prompt should be blocked.
        Returns: (is_blocked, response_message)
        """
        is_blocked = self.blocklist.is_blocked(prompt)

        if is_blocked:
            categories = self.blocklist.get_blocked_categories(prompt)

            for cat in categories:
                cat_type = cat.replace('_es', '').replace('_en', '')
                if cat_type in self.RESPONSES:
                    self.logger.warning(f"Blocked prompt: {cat_type}")
                    return True, self.RESPONSES[cat_type]

            self.logger.warning(f"Blocked prompt: general")
            return True, self.DEFAULT_RESPONSE

        return False, None

    def filter(self, prompt: str) -> str:
        """Filter prompt, return safe version or block message."""
        is_blocked, response = self.check(prompt)

        if is_blocked:
            self._log_blocked(prompt, response)
            return response

        return prompt

    def _log_blocked(self, prompt: str, response: str) -> None:
        """Log blocked request."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'input',
            'prompt_preview': prompt[:100],
            'response': response[:100],
        }
        self.logger.info(json.dumps(entry))