"""
Test script for the document processor.
"""
from pathlib import Path
from src.core.document_processor import DocumentProcessor


def test_document_processor():
    """Test loading and splitting a PDF file."""

    # Initialize the processor
    processor = DocumentProcessor()

    # Check if we have any PDF files in the documents directory
    documents_dir = Path("data/documents")

    if not documents_dir.exists():
        print("Creating documents directory...")
        documents_dir.mkdir(parents=True, exist_ok=True)
        print("Please add some PDF files to data/documents/ and run this script again")
        return

    # Find PDF files
    pdf_files = list(documents_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/documents/")
        print("Please add some PDF files and run this script again")
        return

    # Test with the first PDF file
    test_file = pdf_files[0]
    print(f"Testing with file: {test_file}")

    try:
        # Test the complete processing pipeline
        chunks = processor.process_pdf(test_file)

        print(f"\n=== PROCESSING RESULTS ===")
        print(f"Total chunks created: {len(chunks)}")

        # Show first few chunks
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Content (first 150 chars): {chunk.page_content[:150]}...")
            print(f"Metadata: {chunk.metadata}")

        if len(chunks) > 3:
            print(f"\n... and {len(chunks) - 3} more chunks")

    except Exception as e:
        print(f"Error processing PDF: {e}")


if __name__ == "__main__":
    test_document_processor()
