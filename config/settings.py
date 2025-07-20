import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"

# Vector database settings
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# Document processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embedding model settings
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# LLM settings (using free local model)
LLM_MODEL = "mistral"  # or "llama2", "codellama", etc.
