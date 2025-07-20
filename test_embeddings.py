"""
Test script for the embedding manager.
"""
from pathlib import Path
from src.core.document_processor import DocumentProcessor
from src.core.embedding_manager import EmbeddingManager


def test_embedding_manager():
    """Test the embedding manager with sample documents."""

    # Initialize managers
    doc_processor = DocumentProcessor()
    embedding_manager = EmbeddingManager()

    # Check if we have any PDF files
    documents_dir = Path("data/documents")
    pdf_files = list(documents_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/documents/")
        print("Please add some PDF files and run this script again")
        return

    # Test with the first PDF file
    test_file = pdf_files[0]
    print(f"Testing with file: {test_file}")

    try:
        # Process the document
        chunks = doc_processor.process_pdf(test_file)
        print(f"Created {len(chunks)} chunks from document")

        # Create embeddings
        vectorstore = embedding_manager.create_embeddings(chunks)

        # Test similarity search
        print("\n=== TESTING SIMILARITY SEARCH ===")
        query = "What is this document about?"
        results = vectorstore.similarity_search(query, k=2)

        print(f"Query: {query}")
        print(f"Found {len(results)} similar documents:")

        for i, result in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(f"Content: {result.page_content[:200]}...")
            print(f"Source: {result.metadata.get('source_file', 'Unknown')}")

    except Exception as e:
        print(f"Error testing embeddings: {e}")


if __name__ == "__main__":
    test_embedding_manager()
