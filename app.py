"""
Streamlit web interface for the RAG file assistant.
"""
import streamlit as st
import os
from pathlib import Path
import tempfile
import shutil
from src.core.document_processor import DocumentProcessor
from src.core.embedding_manager import EmbeddingManager
from src.core.rag_engine import RAGEngine

# Page configuration
st.set_page_config(
    page_title="RAG File Assistant",
    page_icon="📚",
    layout="wide"
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None
    if 'documents_processed' not in st.session_state:
        st.session_state.documents_processed = False
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []


def ensure_documents_directory():
    """Ensure the documents directory exists."""
    documents_dir = Path("data/documents")
    documents_dir.mkdir(parents=True, exist_ok=True)
    return documents_dir


def clear_chroma_db():
    """Clear the ChromaDB to remove old embeddings."""
    chroma_dir = Path("data/chroma_db")
    if chroma_dir.exists():
        try:
            shutil.rmtree(chroma_dir)
            st.success("Cleared old embeddings database")
            return True
        except Exception as e:
            st.error(f"Error clearing embeddings: {str(e)}")
            return False
    return True


def save_uploaded_file(uploaded_file):
    """Save an uploaded file to the documents directory."""
    documents_dir = ensure_documents_directory()

    # Create a safe filename
    filename = uploaded_file.name
    file_path = documents_dir / filename

    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def process_documents(force_rebuild=False):
    """Process documents and create embeddings."""
    with st.spinner("Processing documents..."):
        try:
            # Clear old embeddings if force rebuild
            if force_rebuild:
                clear_chroma_db()

            # Initialize processors
            doc_processor = DocumentProcessor()
            embedding_manager = EmbeddingManager()

            # Get documents from the documents directory
            documents_dir = Path("data/documents")
            pdf_files = list(documents_dir.glob("*.pdf"))

            if not pdf_files:
                st.error("No PDF files found in data/documents/")
                return False

            # Process all PDF files
            all_chunks = []
            for pdf_file in pdf_files:
                st.info(f"Processing: {pdf_file.name}")
                chunks = doc_processor.process_pdf(pdf_file)
                all_chunks.extend(chunks)

            # Create embeddings
            st.info("Creating embeddings...")
            vectorstore = embedding_manager.create_embeddings(all_chunks)

            if vectorstore is None:
                st.error("Failed to create embeddings. Please try again.")
                return False

            # Store in session state
            st.session_state.vectorstore = vectorstore
            st.session_state.documents_processed = True

            st.success(f"Successfully processed {len(pdf_files)} documents!")
            return True

        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")

            # Try to recover from database errors
            if "readonly database" in str(e).lower() or "database error" in str(e).lower():
                st.warning("Database error detected. Attempting to fix...")
                try:
                    # Clear the database completely
                    clear_chroma_db()
                    st.info(
                        "Database cleared. Please try processing documents again.")
                except Exception as clear_error:
                    st.error(f"Failed to clear database: {str(clear_error)}")

            return False


def setup_rag_engine():
    """Initialize the RAG engine."""
    if st.session_state.vectorstore is not None:
        with st.spinner("Initializing RAG engine..."):
            try:
                rag_engine = RAGEngine(st.session_state.vectorstore)
                st.session_state.rag_engine = rag_engine
                st.success("RAG engine ready!")
                return True
            except Exception as e:
                st.error(f"Error initializing RAG engine: {str(e)}")
                return False
    return False


def get_available_files():
    """Get list of available files for filtering."""
    documents_dir = Path("data/documents")
    pdf_files = list(documents_dir.glob("*.pdf"))
    return [f.name for f in pdf_files]


def handle_file_upload():
    """Handle file uploads and save them."""
    st.subheader("📁 Upload Documents")

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files to upload",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF files. You can select multiple files at once."
    )

    if uploaded_files:
        # Show uploaded files
        st.write("**Uploaded files:**")
        for uploaded_file in uploaded_files:
            st.write(f"• {uploaded_file.name} ({uploaded_file.size} bytes)")

        # Save files button
        if st.button("💾 Save Uploaded Files", type="primary"):
            saved_files = []
            for uploaded_file in uploaded_files:
                try:
                    file_path = save_uploaded_file(uploaded_file)
                    saved_files.append(file_path.name)
                    st.success(f"Saved: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error saving {uploaded_file.name}: {str(e)}")

            if saved_files:
                st.session_state.uploaded_files.extend(saved_files)
                st.success(f"Successfully saved {len(saved_files)} files!")

                # Auto-process documents after upload
                if st.button("🔄 Process New Documents", type="secondary"):
                    if process_documents(force_rebuild=True):
                        setup_rag_engine()


def show_document_management():
    """Show document management section."""
    st.subheader("📋 Document Management")

    # Show existing files
    documents_dir = Path("data/documents")
    existing_files = list(documents_dir.glob("*.pdf"))

    if existing_files:
        st.write("**Existing documents:**")
        for file in existing_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"• {file.name}")
            with col2:
                st.write(f"({file.stat().st_size / 1024:.1f} KB)")
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{file.name}"):
                    try:
                        file.unlink()
                        st.success(f"Deleted {file.name}")
                        # Clear embeddings after file deletion
                        st.session_state.documents_processed = False
                        st.session_state.vectorstore = None
                        st.session_state.rag_engine = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting {file.name}: {str(e)}")
    else:
        st.info("No documents uploaded yet.")

    # Clear all documents button
    if existing_files:
        if st.button("🗑️ Clear All Documents", type="secondary"):
            try:
                for file in existing_files:
                    file.unlink()
                st.success("All documents cleared!")
                # Clear embeddings after clearing all documents
                st.session_state.documents_processed = False
                st.session_state.vectorstore = None
                st.session_state.rag_engine = None
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing documents: {str(e)}")

    # Rebuild embeddings button
    st.markdown("---")
    st.subheader("🔄 Rebuild Embeddings")
    st.markdown("""
    **When to rebuild embeddings:**
    - After deleting files
    - When embeddings seem outdated
    - If you're getting answers from deleted files
    """)

    if st.button("🔄 Rebuild Embeddings", type="primary"):
        if process_documents(force_rebuild=True):
            setup_rag_engine()


def main():
    """Main application."""
    st.title("📚 RAG File Assistant")
    st.markdown("Ask questions about your documents using AI!")

    # Initialize session state
    initialize_session_state()

    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(
        ["📤 Upload & Process", "❓ Ask Questions", "📋 Manage Documents"])

    with tab1:
        st.header("📤 Upload & Process Documents")

        # File upload section
        handle_file_upload()

        st.markdown("---")

        # Manual processing section
        st.subheader("🔄 Process Documents")
        st.markdown("""
        **Option 1: Upload files above and auto-process**

        **Option 2: Manual processing**
        - Add PDF files to `data/documents/` folder
        - Click the button below
        """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Process Documents", type="primary"):
                if process_documents():
                    setup_rag_engine()

        with col2:
            if st.button("🔄 Rebuild All Embeddings", type="secondary"):
                if process_documents(force_rebuild=True):
                    setup_rag_engine()

        if st.session_state.documents_processed:
            st.success("✅ Documents processed and ready!")
        else:
            st.warning("⚠️ Documents not processed yet")

    with tab2:
        st.header("❓ Ask Questions")

        if not st.session_state.documents_processed:
            st.info(
                "👆 Please upload and process documents first in the 'Upload & Process' tab.")
            return

        if st.session_state.rag_engine is None:
            st.info("🔄 Initializing RAG engine...")
            if not setup_rag_engine():
                st.error("Failed to initialize RAG engine")
                return

        # File filtering
        st.subheader("📁 Document Filter")
        available_files = get_available_files()

        col1, col2 = st.columns([3, 1])
        with col1:
            file_filter = st.selectbox(
                "Search in specific document (optional):",
                ["All Documents"] + available_files,
                help="Select a specific document to search in, or 'All Documents' to search everything"
            )

        with col2:
            if st.button("🔍 Show Available Files"):
                st.write("**Available files:**")
                for file in available_files:
                    st.write(f"• {file}")

        # Question input with examples
        question = st.text_input(
            "Enter your question:",
            placeholder="e.g., What is Nike's revenue in 2023? OR Summarize my experience from my resume"
        )

        # Example questions
        st.markdown("**Example questions:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("💰 Revenue"):
                st.session_state.example_question = "What is Nike's revenue in 2023?"
        with col2:
            if st.button("🏢 Distribution"):
                st.session_state.example_question = "How many distribution centers does Nike have?"
        with col3:
            if st.button("📊 Summary"):
                st.session_state.example_question = "Summarize Nike's business model"
        with col4:
            if st.button("👤 My Experience"):
                st.session_state.example_question = "Summarize my experience from my resume"

        # Use example question if selected
        if 'example_question' in st.session_state:
            question = st.session_state.example_question
            del st.session_state.example_question

        # Process question
        if question:
            with st.spinner("Thinking..."):
                try:
                    # Determine file filter
                    selected_filter = None
                    if file_filter != "All Documents":
                        selected_filter = file_filter

                    result = st.session_state.rag_engine.ask_question(
                        question, selected_filter)

                    # Display answer
                    st.markdown("### Answer")
                    st.write(result['answer'])

                    # Display template and filter info
                    col1, col2 = st.columns(2)
                    with col1:
                        if 'template_used' in result:
                            st.info(
                                f"Template used: {result['template_used']}")
                    with col2:
                        if 'file_filter' in result and result['file_filter']:
                            st.info(f"Filtered for: {result['file_filter']}")

                    # Display sources
                    if result['sources']:
                        st.markdown("### Sources")
                        for i, source in enumerate(result['sources'], 1):
                            with st.expander(f"Source {i}: {Path(source['source']).name}"):
                                st.write(f"**Content:** {source['content']}")
                                st.write(f"**File:** {source['source']}")
                                if source.get('page'):
                                    st.write(f"**Page:** {source['page']}")

                except Exception as e:
                    st.error(f"Error processing question: {str(e)}")

    with tab3:
        st.header("📋 Manage Documents")
        show_document_management()


if __name__ == "__main__":
    main()
