#!/usr/bin/env python3
"""
P.I.I. Scrubber for EPUB Content
Removes personal identifiable information from text.
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Tuple


class PIIScrubber:
    """Remove PII from text content."""

    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(\+?34\s?)?(\d{3}[\s-]?\d{3}[\s-]?\d{3}|\d{9})\b',
        'dni': r'\b\d{8}[A-Z]\b',
        'ssn': r'\b\d{8,9}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    }

    REPLACEMENTS = {
        'email': '[EMAIL]',
        'phone': '[TELÉFONO]',
        'dni': '[DNI]',
        'ssn': '[NÚMERO_SS]',
        'credit_card': '[TARJETA]',
    }

    def __init__(self, log_path: str = "logs/pii_scrub.log"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.findings = []

    def scrub_text(self, text: str) -> Tuple[str, List[str]]:
        """Scrub PII from text."""
        findings = []
        scrubbed = text

        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, scrubbed)
            if matches:
                findings.append(f"{pii_type}: {len(matches)} instances")
                scrubbed = re.sub(pattern, self.REPLACEMENTS[pii_type], scrubbed)

        return scrubbed, findings

    def scrub_jsonl(self, input_path: str, output_path: str) -> int:
        """Scrub PII from JSONL file."""
        if not Path(input_path).exists():
            print(f"Error: File not found: {input_path}")
            return 1

        count = 0
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:

            for line in infile:
                data = json.loads(line)
                original_text = data.get('text', '')

                scrubbed_text, findings = self.scrub_text(original_text)

                if findings:
                    self.findings.append({
                        'line': count,
                        'findings': findings
                    })

                data['text'] = scrubbed_text
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                count += 1

        self._save_log()
        print(f"Scrubbed {count} entries")
        return 0

    def _save_log(self) -> None:
        """Save scrub log."""
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write("P.I.I. Scrub Log\n")
            f.write("=" * 50 + "\n\n")
            for item in self.findings:
                f.write(f"Line {item['line']}: {', '.join(item['findings'])}\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: python clean_pii.py <input.jsonl> <output.jsonl>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    scrubber = PIIScrubber()
    sys.exit(scrubber.scrub_jsonl(input_file, output_file))


if __name__ == "__main__":
    main()