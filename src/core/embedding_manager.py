"""
Embedding manager for creating and storing document embeddings.
"""
import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb
from chromadb.config import Settings
import gc

from config.settings import EMBEDDING_MODEL, CHROMA_DB_DIR


class EmbeddingManager:
    # Manages document embeddings using HuggingFace and ChromaDB.

    def __init__(self):
        print("Initializing embedding manager...")

        # Initialize HuggingFace embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"Loaded embedding model: {EMBEDDING_MODEL}")

        # Ensure ChromaDB directory exists
        self.chroma_dir = Path(CHROMA_DB_DIR)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

    def _clear_chroma_db(self):
        """Clear the ChromaDB to avoid conflicts."""
        try:
            # Remove the entire ChromaDB directory
            if self.chroma_dir.exists():
                import shutil
                shutil.rmtree(self.chroma_dir)
                print(f"Cleared ChromaDB at {self.chroma_dir}")

            # Recreate the directory
            self.chroma_dir.mkdir(parents=True, exist_ok=True)

            # Force garbage collection to clean up any lingering references
            gc.collect()

            return True
        except Exception as e:
            print(f"Error clearing ChromaDB: {e}")
            return False

    def _create_chroma_client(self):
        """Create a fresh ChromaDB client."""
        try:
            # Clear any existing connections and force garbage collection
            gc.collect()

            # Create client with unique settings
            client = chromadb.PersistentClient(
                path=str(self.chroma_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            return client
        except Exception as e:
            print(f"Error creating ChromaDB client: {e}")
            # Try clearing and recreating
            self._clear_chroma_db()
            gc.collect()
            return chromadb.PersistentClient(
                path=str(self.chroma_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )

    def create_embeddings(self, documents: List[Document]) -> Chroma:
        """Create embeddings for documents and store in ChromaDB."""
        if not documents:
            print("No documents to process")
            return None

        print(f"Creating embeddings for {len(documents)} documents...")

        try:
            # Clear existing ChromaDB to avoid conflicts
            self._clear_chroma_db()

            # Force garbage collection
            gc.collect()

            # Create fresh ChromaDB client
            client = self._create_chroma_client()

            # Create vectorstore with fresh client and unique collection name
            import time
            collection_name = f"documents_{int(time.time())}"

            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                client=client,
                collection_name=collection_name
            )

            print(
                f"Successfully created embeddings and stored in {self.chroma_dir}")
            return vectorstore

        except Exception as e:
            print(f"Error creating embeddings: {e}")

            # Try one more time with complete reset
            try:
                print("Attempting complete reset...")
                self._clear_chroma_db()
                gc.collect()
                client = self._create_chroma_client()

                import time
                collection_name = f"documents_{int(time.time())}"

                vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    client=client,
                    collection_name=collection_name
                )

                print(f"Successfully created embeddings after reset")
                return vectorstore

            except Exception as e2:
                print(f"Failed to create embeddings after reset: {e2}")
                raise e2

    def load_existing_vectorstore(self) -> Chroma:
        """Load existing vectorstore from ChromaDB."""
        try:
            # Create client
            client = self._create_chroma_client()

            # Get all collections
            collections = client.list_collections()

            if not collections:
                print("No existing collections found")
                return None

            # Use the first available collection
            collection_name = collections[0].name

            # Load existing vectorstore
            vectorstore = Chroma(
                client=client,
                collection_name=collection_name,
                embedding_function=self.embeddings
            )

            # Test if it has documents
            collection = client.get_collection(collection_name)
            count = collection.count()
            print(f"Loaded existing vectorstore with {count} documents")

            return vectorstore

        except Exception as e:
            print(f"Error loading existing vectorstore: {e}")
            return None
