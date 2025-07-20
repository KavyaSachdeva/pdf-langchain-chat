"""
Test script to compare different prompt templates.
"""
from pathlib import Path
from src.core.document_processor import DocumentProcessor
from src.core.embedding_manager import EmbeddingManager
from src.core.rag_engine import RAGEngine


def test_different_templates():
    """Test how different templates handle the same question."""

    print("=== TEMPLATE COMPARISON TEST ===")

    # Check if we have any PDF files
    documents_dir = Path("data/documents")
    pdf_files = list(documents_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/documents/")
        return

    # Test with the first PDF file
    test_file = pdf_files[0]
    print(f"Testing with file: {test_file}")

    try:
        # Process document and create embeddings
        doc_processor = DocumentProcessor()
        chunks = doc_processor.process_pdf(test_file)

        embedding_manager = EmbeddingManager()
        vectorstore = embedding_manager.create_embeddings(chunks)

        # Initialize RAG engine
        rag_engine = RAGEngine(vectorstore)

        # Test questions that should trigger different templates
        test_questions = [
            "What is Nike's revenue in 2023?",  # Financial template
            "Summarize Nike's business model",   # Summary template
            "Compare Nike's performance in different regions",  # Comparison template
            "How many distribution centers does Nike have?",  # Basic template
        ]

        for question in test_questions:
            print(f"\n{'='*50}")
            print(f"Question: {question}")
            print(f"{'='*50}")

            result = rag_engine.ask_question(question)

            print(f"Template Used: {result['template_used']}")
            print(f"Answer: {result['answer']}")
            print(f"Sources: {len(result['sources'])} documents")

    except Exception as e:
        print(f"Error testing templates: {e}")


if __name__ == "__main__":
    test_different_templates()
