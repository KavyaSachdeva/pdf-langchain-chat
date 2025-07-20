# Deployment Guide for RAG File Assistant

This guide covers how to deploy the RAG File Assistant to different platforms.

## 🚀 Quick Deploy Options

### 1. Streamlit Cloud (Recommended for Beginners)

**Pros:**

- Free tier available
- Easy deployment
- Automatic updates from GitHub
- Built-in file upload support

**Steps:**

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set the path to `app.py`
5. Deploy!

**Environment Variables (if needed):**

```
LLM_MODEL=mistral
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

### 2. Railway

**Pros:**

- Free tier available
- Easy deployment
- Good for small projects

**Steps:**

1. Install Railway CLI: `npm install -g @railway/cli`
2. Create `railway.json`:

```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
  }
}
```

3. Deploy: `railway up`

### 3. Heroku

**Pros:**

- Reliable
- Good documentation

**Steps:**

1. Create `Procfile`:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Create `setup.sh`:

```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
" > ~/.streamlit/config.toml
```

3. Update `requirements.txt` with all dependencies
4. Deploy: `heroku create && git push heroku main`

### 4. Docker Deployment

**For advanced users who want full control:**

1. Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p data/documents data/chroma_db

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. Create `docker-compose.yml`:

```yaml
version: "3.8"
services:
  rag-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - LLM_MODEL=mistral
      - EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

3. Deploy:

```bash
docker-compose up --build
```

## 🔧 Pre-deployment Checklist

### 1. Update Requirements

Make sure your `requirements.txt` includes all dependencies:

```txt
streamlit>=1.28.0
langchain>=0.1.0
langchain-community>=0.0.10
langchain-core>=0.1.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
pypdf>=3.15.0
```

### 2. Environment Setup

Create a `.env` file for local development:

```env
LLM_MODEL=mistral
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
CHROMA_DB_DIR=data/chroma_db
DOCUMENTS_DIR=data/documents
```

### 3. File Structure

Ensure your project structure is correct:

```
rag-file-assistant/
├── app.py
├── requirements.txt
├── config/
│   └── settings.py
├── src/
│   └── core/
│       ├── document_processor.py
│       ├── embedding_manager.py
│       ├── rag_engine.py
│       └── prompt_templates.py
└── data/
    ├── documents/
    └── chroma_db/
```

## 🌐 Production Considerations

### 1. Security

- Add authentication if needed
- Limit file upload sizes
- Validate file types
- Use HTTPS in production

### 2. Performance

- Consider using a more powerful LLM for production
- Implement caching for embeddings
- Use a proper database instead of file storage
- Add rate limiting

### 3. Monitoring

- Add logging
- Monitor memory usage
- Track user interactions
- Set up alerts

## 🔄 Continuous Deployment

### GitHub Actions (for Streamlit Cloud)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Streamlit Cloud
        run: |
          # Streamlit Cloud auto-deploys from GitHub
          echo "Deployment triggered"
```

## 📊 Usage Analytics

Add analytics to track usage:

```python
# In app.py
import streamlit as st

# Track page views
if 'page_views' not in st.session_state:
    st.session_state.page_views = 0
st.session_state.page_views += 1

# Track questions asked
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = 0
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Port already in use:**

   ```bash
   lsof -ti:8501 | xargs kill -9
   ```

2. **Memory issues:**

   - Reduce chunk size in settings
   - Use smaller embedding model
   - Implement pagination

3. **File upload issues:**

   - Check file permissions
   - Ensure directory exists
   - Validate file types

4. **LLM not responding:**
   - Check Ollama is running
   - Verify model is downloaded
   - Check network connectivity

## 📈 Scaling Considerations

### For High Traffic:

1. **Use a proper database** (PostgreSQL, MongoDB)
2. **Implement caching** (Redis)
3. **Use a CDN** for static files
4. **Load balancing** for multiple instances
5. **Background processing** for document processing

### For Large Documents:

1. **Implement chunking strategies**
2. **Use streaming responses**
3. **Add progress indicators**
4. **Implement retry logic**

## 🎯 Next Steps

After deployment:

1. Test the application thoroughly
2. Monitor performance and usage
3. Gather user feedback
4. Implement improvements based on usage patterns
5. Consider adding authentication if needed
6. Plan for scaling as usage grows
