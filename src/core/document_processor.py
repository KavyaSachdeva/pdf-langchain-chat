"""
Document processor for loading and chunking files.
"""
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentProcessor:
    """Handles loading and processing of documents."""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            add_start_index=True
        )
        print("Document processor initialized")

    def load_pdf(self, file_path: Path) -> List[Document]:
        """Load a PDF file and return documents."""
        print(f"Loading PDF: {file_path}")

        loader = PyPDFLoader(str(file_path))
        documents = loader.load()

        print(f"Loaded {len(documents)} pages from {file_path.name}")
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks."""
        print(f"Splitting {len(documents)} documents into chunks...")

        chunks = self.text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")

        return chunks

    def process_pdf(self, file_path: Path) -> List[Document]:
        """Load and split a PDF file."""
        # Load the PDF
        documents = self.load_pdf(file_path)

        # Split into chunks
        chunks = self.split_documents(documents)

        # Add file metadata to each chunk
        for chunk in chunks:
            chunk.metadata['source_file'] = str(file_path)
            chunk.metadata['file_type'] = 'pdf'

        return chunks
