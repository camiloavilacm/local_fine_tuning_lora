#!/usr/bin/env python3
"""
EPUB to JSONL Converter for Fine-Tuning
Converts Spanish EPUB books to MLX fine-tuning format.
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Please install dependencies: pip install ebooklib beautifulsoup4")
    sys.exit(1)


class EPUBConverter:
    """Convert EPUB books to JSONL training format."""

    MIN_CHAPTER_LENGTH = 500

    def __init__(self, epub_path: str, output_path: str):
        self.epub_path = Path(epub_path)
        self.output_path = Path(output_path)
        self.book_title = ""
        self.author = ""

    def extract_book_metadata(self, book) -> None:
        """Extract title and author from EPUB."""
        self.book_title = book.get_metadata('DC', 'title')
        self.book_title = self.book_title[0][0] if self.book_title else "Unknown"

        self.author = book.get_metadata('DC', 'creator')
        self.author = self.author[0][0] if self.author else "Unknown"

        print(f"Book: {self.book_title}")
        print(f"Author: {self.author}")

    def clean_html(self, html_content: str) -> str:
        """Remove HTML tags and clean text."""
        soup = BeautifulSoup(html_content, 'html.parser')

        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator=' ')
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def extract_chapters(self, book) -> List[Dict[str, str]]:
        """Extract all chapters from the EPUB."""
        chapters = []

        for item in book.get_items():
            if item.get_type() == 9:
                content = item.get_content().decode('utf-8')
                text = self.clean_html(content)

                chapter_name = item.get_name()
                if len(text) >= self.MIN_CHAPTER_LENGTH:
                    chapters.append({
                        'title': chapter_name,
                        'content': text
                    })

        return chapters

    def create_training_entry(self, content: str, title: str) -> Dict[str, str]:
        """Create MLX training format entry."""
        text = f"<|user|>{self.book_title}<|assistant|>{title}\n{content}"
        return {"text": text}

    def convert(self) -> int:
        """Main conversion function."""
        if not self.epub_path.exists():
            print(f"Error: File not found: {self.epub_path}")
            return 1

        print(f"Loading EPUB: {self.epub_path}")
        book = epub.read_epub(str(self.epub_path))

        self.extract_book_metadata(book)
        chapters = self.extract_chapters(book)

        print(f"Found {len(chapters)} valid chapters")

        with open(self.output_path, 'w', encoding='utf-8') as f:
            for chapter in chapters:
                entry = self.create_training_entry(
                    chapter['content'],
                    chapter['title']
                )
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        print(f"Output saved to: {self.output_path}")
        print(f"Total entries: {len(chapters)}")
        return 0


def main():
    if len(sys.argv) < 3:
        print("Usage: python convert.py <input.epub> <output.jsonl>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    converter = EPUBConverter(input_file, output_file)
    sys.exit(converter.convert())


if __name__ == "__main__":
    main()