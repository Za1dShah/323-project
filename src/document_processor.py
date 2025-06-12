"""
Document processing utilities for the Bank AI Chatbot.
This module handles the extraction of text from various document formats,
chunking the text into manageable pieces, and creating embeddings.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
    nltk.download("punkt_tab")
except LookupError:
    nltk.download('punkt')

from src.config import (
    DOCUMENTS_DIR,
    PROCESSED_DIR,
    EMBEDDINGS_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL
)

class DocumentProcessor:
    """Process documents and create embeddings for the knowledge base."""

    def __init__(self):
        """Initialize the document processor."""
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    def process_all_documents(self) -> Dict[str, int]:
        """
        Process all documents in the documents directory.

        Returns:
            Dict[str, int]: A dictionary with document categories as keys and
                           the number of processed documents as values.
        """
        stats = {}

        for category_dir in DOCUMENTS_DIR.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                processed_count = self._process_category(category_dir, category_name)
                stats[category_name] = processed_count

        return stats

    def _process_category(self, category_dir: Path, category_name: str) -> int:
        """
        Process all documents in a category directory.

        Args:
            category_dir (Path): Path to the category directory.
            category_name (str): Name of the category.

        Returns:
            int: Number of processed documents.
        """
        processed_count = 0

        processed_category_dir = PROCESSED_DIR / category_name
        embeddings_category_dir = EMBEDDINGS_DIR / category_name

        os.makedirs(processed_category_dir, exist_ok=True)
        os.makedirs(embeddings_category_dir, exist_ok=True)

        for doc_path in category_dir.iterdir():
            if doc_path.is_file():
                try:
                    text = self._extract_text(doc_path)

                    if not text.strip():
                        print(f"Warning: Empty document {doc_path}")
                        continue

                    chunks = self._create_chunks(text)

                    processed_path = processed_category_dir / f"{doc_path.stem}.json"
                    with open(processed_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            'source': str(doc_path),
                            'chunks': chunks
                        }, f, indent=2)

                    self._create_embeddings(chunks, doc_path.stem, embeddings_category_dir)

                    processed_count += 1

                except Exception as e:
                    print(f"Error processing {doc_path}: {e}")

        return processed_count

    def _extract_text(self, doc_path: Path) -> str:
        """
        Extract text from a document.

        Args:
            doc_path (Path): Path to the document.

        Returns:
            str: Extracted text.
        """
        suffix = doc_path.suffix.lower()
        if suffix == '.pdf':
            return self._extract_text_from_pdf(doc_path)
        elif suffix == '.docx':
            return self._extract_text_from_docx(doc_path)
        elif suffix in ['.txt', '.md']:
            return self._extract_text_from_text_file(doc_path)
        else:
            raise ValueError(f"Unsupported file format: {doc_path.suffix}")

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from a PDF file using pdftotext.

        Args:
            pdf_path (Path): Path to the PDF file.

        Returns:
            str: Extracted text.
        """
        try:
            result = subprocess.run(
                ['pdftotext', str(pdf_path), '-'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            print(f"Warning: Could not extract text from {pdf_path} using pdftotext")
            return f"[PDF EXTRACTION FAILED: {pdf_path}]"

    def _extract_text_from_docx(self, docx_path: Path) -> str:
        """
        Extract text from a DOCX file.

        Args:
            docx_path (Path): Path to the DOCX file.

        Returns:
            str: Extracted text.
        """
        try:
            import docx
        except ImportError:
            print("Warning: python-docx not installed. Installing...")
            subprocess.run(['pip', 'install', 'python-docx'], check=True)
            import docx

        doc = docx.Document(docx_path)
        return '\n\n'.join([para.text for para in doc.paragraphs])

    def _extract_text_from_text_file(self, text_path: Path) -> str:
        """
        Extract text from a text file.

        Args:
            text_path (Path): Path to the text file.

        Returns:
            str: Extracted text.
        """
        with open(text_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.

        Args:
            text (str): Text to split.

        Returns:
            List[Dict[str, Any]]: List of chunks with metadata.
        """
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = sent_tokenize(text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > CHUNK_SIZE and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'size': len(current_chunk)
                })

                words = current_chunk.split()
                overlap_word_count = max(1, int(CHUNK_OVERLAP / 10))
                overlap_words = words[-overlap_word_count:] if len(words) > overlap_word_count else words
                current_chunk = ' '.join(overlap_words) + ' ' + sentence
            else:
                current_chunk += ' ' + sentence

        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'size': len(current_chunk)
            })

        return chunks

    def _create_embeddings(self, chunks: List[Dict[str, Any]], doc_name: str, output_dir: Path) -> None:
        """
        Create embeddings for chunks and save them.

        Args:
            chunks (List[Dict[str, Any]]): List of text chunks.
            doc_name (str): Document name.
            output_dir (Path): Output directory.
        """
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts)

        embeddings_path = output_dir / f"{doc_name}.json"
        with open(embeddings_path, 'w', encoding='utf-8') as f:
            json.dump({
                'document': doc_name,
                'embeddings': embeddings.tolist()
            }, f)



if __name__ == "__main__":
    processor = DocumentProcessor()
    stats = processor.process_all_documents()
    print(f"Processed documents: {stats}")
