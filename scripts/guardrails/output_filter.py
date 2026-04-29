"""
Output Guardrail - Filter model responses before returning to user
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from .blocklist import Blocklist


class OutputGuardrail:
    """Filter model output for safety."""

    DEFAULT_RESPONSE = "Lo siento, no puedo generar esa respuesta. ¿Podrías intentar con otra pregunta?"

    RESPONSES = {
        'violence': "No puedo generar contenido violento.",
        'hate': "No puedo generar contenido de odio.",
        'self_harm': "No puedo generar contenido relacionado con autolesión.",
        'sexual': "No puedo generar contenido sexual explícito.",
        'illegal': "No puedo generar contenido sobre actividades ilegales.",
    }

    def __init__(self, log_path: str = "logs/guardrails_output.log"):
        self.blocklist = Blocklist()
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging."""
        self.logger = logging.getLogger('output_guardrail')
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.log_path)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)

    def check(self, response: str) -> tuple[bool, Optional[str]]:
        """
        Check if response should be blocked.
        Returns: (is_blocked, replacement_message)
        """
        import re
        response = re.sub(r'<\|[^|]*\|>', '', response).strip()
        response = re.sub(r'<\|.*', '', response).strip()
        response = re.sub(r'Usuario:.*', '', response).strip()
        response = re.sub(r'\nUsuario:.*', '', response).strip()
        
        is_blocked = self.blocklist.is_blocked(response)

        if is_blocked:
            categories = self.blocklist.get_blocked_categories(response)

            for cat in categories:
                cat_type = cat.replace('_es', '').replace('_en', '')
                if cat_type in self.RESPONSES:
                    self.logger.warning(f"Blocked output: {cat_type}")
                    return True, self.RESPONSES[cat_type]

            self.logger.warning(f"Blocked output: general")
            return True, self.DEFAULT_RESPONSE

        return False, response

    def filter(self, response: str) -> str:
        """Filter response, return safe version or block message."""
        is_blocked, replacement = self.check(response)

        if is_blocked:
            self._log_blocked(response, replacement)
            return replacement

        return response

    def _log_blocked(self, response: str, replacement: str) -> None:
        """Log blocked response."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'output',
            'response_preview': response[:100],
            'replacement': replacement[:100],
        }
        self.logger.info(json.dumps(entry))