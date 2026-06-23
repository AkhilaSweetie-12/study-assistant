import os
import hashlib
from typing import List, Dict, Any

import pypdf


class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _load_pdf(self, file_path: str) -> str:
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    def _load_text_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _chunk_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_content = text[start:end].strip()

            if chunk_content:
                chunk_id = hashlib.md5(f"{source}_{chunk_index}".encode()).hexdigest()
                chunks.append(
                    {
                        "id": chunk_id,
                        "content": chunk_content,
                        "source": source,
                        "chunk_index": chunk_index,
                    }
                )
                chunk_index += 1

            start = end - self.chunk_overlap

        return chunks

    def process_study_document(self, file_path: str) -> List[Dict[str, Any]]:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        text = self._load_pdf(file_path) if ext == ".pdf" else self._load_text_file(file_path)

        chunks = self._chunk_text(text, filename)
        for chunk in chunks:
            chunk["title"] = filename

        return chunks

    def process_code_document(self, file_path: str) -> List[Dict[str, Any]]:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".md": "markdown",
            ".txt": "text",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
        }
        language = language_map.get(ext, "text")

        text = self._load_text_file(file_path)
        chunks = self._chunk_text(text, filename)

        for chunk in chunks:
            chunk["filename"] = filename
            chunk["language"] = language

        return chunks
