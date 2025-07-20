"""
RAG Engine that combines vector search with LLM for question answering.
"""
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from config.settings import LLM_MODEL
from .prompt_templates import BASIC_QA_TEMPLATE, FINANCIAL_TEMPLATE, SUMMARY_TEMPLATE, COMPARISON_TEMPLATE


class RAGEngine:
    """Main RAG engine for question answering."""

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

        # Initialize local LLM via Ollama
        self.llm = Ollama(
            model=LLM_MODEL,
            temperature=0.1  # Low temperature for factual answers
        )

        # Store templates
        self.templates = {
            "basic": BASIC_QA_TEMPLATE,
            "financial": FINANCIAL_TEMPLATE,
            "summary": SUMMARY_TEMPLATE,
            "comparison": COMPARISON_TEMPLATE
        }

        print(f"RAG Engine initialized with {LLM_MODEL}")

    def _select_template(self, question: str) -> PromptTemplate:
        """Select the appropriate template based on question type."""
        question_lower = question.lower()

        # Financial analysis keywords
        financial_keywords = ["revenue", "profit", "earnings",
                              "financial", "income", "sales", "growth", "percentage", "%"]
        if any(keyword in question_lower for keyword in financial_keywords):
            return self.templates["financial"]

        # Summary keywords
        summary_keywords = ["summarize", "summary",
                            "overview", "brief", "main points"]
        if any(keyword in question_lower for keyword in summary_keywords):
            return self.templates["summary"]

        # Comparison keywords
        comparison_keywords = ["compare", "versus",
                               "vs", "difference", "similar", "different"]
        if any(keyword in question_lower for keyword in comparison_keywords):
            return self.templates["comparison"]

        # Default to basic Q&A
        return self.templates["basic"]

    def _extract_file_filter(self, question: str) -> str:
        """Extract file filter from question."""
        question_lower = question.lower()

        # Common file indicators
        file_indicators = {
            "resume": ["resume", "cv", "my resume", "my cv"],
            "nike": ["nike", "10k", "10-k", "annual report"],
            "research": ["research", "research report"],
            "business plan": ["business plan", "cozad", "plan"]
        }

        for file_type, keywords in file_indicators.items():
            if any(keyword in question_lower for keyword in keywords):
                return file_type

        return None

    def ask_question(self, question: str, file_filter: str = None) -> Dict[str, Any]:
        """Ask a question and get an answer with sources."""
        print(f"Processing question: {question}")

        try:
            # Extract file filter from question if not provided
            if not file_filter:
                file_filter = self._extract_file_filter(question)

            # Select appropriate template
            template = self._select_template(question)
            print(f"Using template: {template.__class__.__name__}")

            # Create retriever with optional file filtering
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 6})

            # Apply file filter if specified
            if file_filter:
                print(f"Filtering for file type: {file_filter}")
                # This is a simplified filter - in practice you'd need more sophisticated filtering
                # For now, we'll increase k to get more results and let the LLM handle it
                retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": 8})

            # Create QA chain with selected template
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={
                    "prompt": template
                }
            )

            # Get answer and sources
            result = qa_chain({"query": question})

            answer = result["result"]
            source_documents = result["source_documents"]

            # Filter sources by file type if specified
            if file_filter:
                filtered_sources = []
                for doc in source_documents:
                    source_file = doc.metadata.get("source_file", "").lower()
                    if file_filter.lower() in source_file:
                        filtered_sources.append(doc)

                # If we found filtered sources, use them
                if filtered_sources:
                    source_documents = filtered_sources
                    print(
                        f"Found {len(filtered_sources)} relevant sources from {file_filter}")
                else:
                    print(
                        f"No sources found for {file_filter}, using all sources")

            # Format sources
            sources = []
            for doc in source_documents:
                sources.append({
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source_file", "Unknown"),
                    "page": doc.metadata.get("page", "Unknown")
                })

            return {
                "answer": answer,
                "sources": sources,
                "question": question,
                "template_used": template.__class__.__name__,
                "file_filter": file_filter
            }

        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "question": question,
                "template_used": "error",
                "file_filter": file_filter
            }
