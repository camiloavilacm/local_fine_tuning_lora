"""
Blocklist - Keyword filters for content moderation
Supports Spanish and English.
"""

from typing import Dict, List, Set


class Blocklist:
    """Keyword blocklist for content filtering."""

    BLOCKLISTS: Dict[str, List[str]] = {
        'violence_es': [
            'bomba', 'explosivo', 'arma', 'matar', 'asesinar',
            'atacar', 'apunalar', 'disparar', 'golpear', 'herir', 'tortura',
            'genocidio', 'masacre', 'suicidio', 'autolesión', 'armas',
        ],
        'violence_en': [
            'bomb', 'explosive', 'weapon', 'kill', 'murder',
            'attack', 'stab', 'shoot', 'hit', 'hurt', 'torture', 'genocide',
            'massacre', 'suicide', 'self-harm', 'guns',
        ],
        'hate_es': [
            'odio', 'racismo', 'discriminación', 'xenófobo', 'homófobo',
            'insulto', 'desprecio', 'inferior', 'superior', 'raza', 'género',
        ],
        'hate_en': [
            'hate', 'racism', 'discrimination', 'xenophobic', 'homophobic',
            'insult', 'contempt', 'inferior', 'superior', 'race', 'gender',
        ],
        'self_harm_es': [
            'suicid', 'autolesión', 'hacerse daño', 'quitarse la vida',
            'cortarse', 'arrancarse', 'no vale la pena', 'mejor muerto',
            'hacerme daño', 'terminar con mi vida',
        ],
        'self_harm_en': [
            'suicide', 'self-harm', 'hurt yourself', 'kill yourself',
            'cut yourself', 'not worth living', 'better dead', 'end it all',
            'harm myself', 'take my life',
        ],
        'sexual_es': [
            'pornografía', 'sexo explícito', 'desnudo', 'violación',
            'abuso sexual', 'acoso sexual', 'Contenido para adultos',
        ],
        'sexual_en': [
            'pornography', 'explicit sex', 'nude', 'rape', 'sexual abuse',
            'sexual harassment', 'adult content',
        ],
        'illegal_es': [
            'droga', 'cocaína', 'heroína', 'marihuana', 'traficar', 'robar',
            'estafar', 'phishing', 'malware', 'hackear', 'piratería',
        ],
        'illegal_en': [
            'drug', 'cocaine', 'heroin', 'marijuana', 'trafficking', 'steal',
            'fraud', 'phishing', 'malware', 'hack', 'piracy',
        ],
    }

    def __init__(self):
        self.all_keywords: Set[str] = set()
        for keywords in self.BLOCKLISTS.values():
            self.all_keywords.update(keyword.lower() for keyword in keywords)

    def is_blocked(self, text: str) -> bool:
        """Return True if any blocklist triggers (word boundary matching)."""
        text_lower = text.lower()
        results = self.check(text)
        return any(results.values())

    def check(self, text: str) -> Dict[str, bool]:
        """Check text against all blocklists using word boundaries."""
        text_lower = text.lower()
        import re
        
        results = {}
        for category, keywords in self.BLOCKLISTS.items():
            found = []
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found.append(keyword)
            results[category] = len(found) > 0
        
        return results

    def get_blocked_categories(self, text: str) -> List[str]:
        """Return list of triggered categories."""
        results = self.check(text)
        return [cat for cat, triggered in results.items() if triggered]