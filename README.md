# RAG File Assistant

Ask questions about your PDF documents using local AI. No API keys required.

## What It Does

- Upload PDF files
- Ask questions about the content
- Get AI answers with source citations
- Filter searches to specific documents

## Quick Start

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama and pull Mistral:**

   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull mistral
   ```

3. **Run the app:**

   ```bash
   streamlit run app.py
   ```

4. **Open browser to:** `http://localhost:8501`

## How to Use

1. **Upload & Process tab:** Upload PDF files and process them
2. **Ask Questions tab:** Ask questions about your documents
3. **Manage Documents tab:** Delete files or rebuild embeddings

## How It Works

1. **Document Processing**: Loads PDFs and splits them into chunks
2. **Embedding Creation**: Converts text chunks into numerical vectors
3. **Question Answering**: Finds relevant chunks and uses AI to generate answers

## Example Questions

- "What was the company's revenue growth last quarter?"
- "Summarize the main points from the annual report"
- "What are my key skills and experience?"
- "What methodology was used in this research study?"

## Troubleshooting

- **"ModuleNotFoundError"**: Run `pip install sentence-transformers`
- **"Ollama model not found"**: Run `ollama pull mistral`
- **Database errors**: Go to Manage Documents tab and click "Rebuild Embeddings"
- **No PDF files found**: Add PDF files to `data/documents/` folder

## Project Structure

```
rag-file-assistant/
├── app.py                    # Main web interface
├── src/core/
│   ├── document_processor.py # PDF processing
│   ├── embedding_manager.py  # Vector embeddings
│   ├── rag_engine.py        # Q&A engine
│   └── prompt_templates.py  # Question templates
├── data/documents/          # Your PDF files go here
└── requirements.txt         # Dependencies
```
