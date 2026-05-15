# Embedding Based Semantic Search

This project is a simple semantic search engine built using FastAPI, Streamlit, and Sentence Transformers.

Instead of searching documents using exact keywords, this application searches based on meaning.

For example:

If a user searches for:

"happy"

the system can also return documents related to:
- joyful
- excited
- cheerful

even if the exact word "happy" does not exist in the document.

This is called semantic search.

---

# How the Project Works

The workflow is simple:

1. User types a query in the Streamlit frontend
2. Frontend sends the query to FastAPI backend
3. Backend converts the query into an embedding vector
4. The system compares the query vector with all document vectors
5. Documents are ranked using cosine similarity
6. Top matching results are returned
7. Streamlit displays the results with similarity scores

---

# What Are Embeddings?

Embeddings are numerical representations of text.

Each document is converted into a vector of numbers that captures semantic meaning.

Example:

```text
"The cat is sleeping"
→ [0.21, -0.44, 0.81, ...]
```

Similar meanings produce vectors that are close to each other mathematically.

---

# Why Cosine Similarity?

Cosine similarity measures how similar two vectors are.

It compares direction instead of magnitude, which makes it better for semantic comparison.

Similarity score examples:

- 1.0 → identical meaning
- 0.8 → very similar
- 0.5 → somewhat related
- 0 → unrelated

---

# Technologies Used

Backend:
- FastAPI
- Sentence Transformers
- NumPy
- Scikit-learn

Frontend:
- Streamlit

Embedding Model:
- all-MiniLM-L6-v2

---

# Project Structure

```text
Embedding-Based-Semantic-Search/

backend/
│
├── main.py
├── embedder.py
├── search_engine.py
└── data_loader.py

frontend/
│
└── app.py

data/
│
└── documents.json

embeddings/
│
└── index.npy

utils/
│
└── helpers.py

requirements.txt
.gitignore
README.md
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/your-username/Embedding-Based-Semantic-Search.git
```

Move into the project folder:

```bash
cd Embedding-Based-Semantic-Search
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment (Git Bash on Windows):

```bash
source venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Project

You need two terminals.

---

# Terminal 1 — Backend

Open Git Bash:

```bash
cd /c/Users/hp/OneDrive/Desktop/embedding-model

source venv/Scripts/activate

cd backend

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

When backend starts successfully, you should see:

```text
Loaded 10 documents successfully
Indexed 10 documents successfully
API ready at http://localhost:8000
```

---

# Terminal 2 — Frontend

Open another Git Bash terminal:

```bash
cd /c/Users/hp/OneDrive/Desktop/embedding-model

source venv/Scripts/activate

streamlit run frontend/app.py
```

Frontend will open in browser automatically.

Usually at:

```text
http://localhost:8501
```

---

# API Flow

```text
User Query
    ↓
Streamlit Frontend
    ↓
POST Request to FastAPI
    ↓
Embedding Generation
    ↓
Cosine Similarity Calculation
    ↓
Ranking Documents
    ↓
Returning Top Results
    ↓
Displaying Results
```

---

# Example Query

```text
machine learning
```

Possible matching documents:
- Deep Learning Basics
- Neural Networks Introduction
- AI Systems Overview

---

# Example API Request

Request:

```json
{
  "query": "machine learning"
}
```

Response:

```json
{
  "results": [
    {
      "document": "Introduction to Deep Learning",
      "score": 0.91
    }
  ]
}
```

---

# Features

- Semantic search
- FastAPI backend
- Streamlit frontend
- Embedding generation
- Cosine similarity ranking
- Top-K retrieval
- Real-time search results

---

# requirements.txt

```txt
fastapi
uvicorn
streamlit
sentence-transformers
numpy
scikit-learn
pydantic
```

---

# .gitignore

```gitignore
venv/
__pycache__/
*.pyc
embeddings/index.npy
```

---

# Future Improvements

Possible future enhancements:
- FAISS integration
- Pinecone vector database
- PDF upload support
- Multi-language search
- Better UI design
- Authentication
- Docker deployment

---

# Learning Outcomes

This project helps understand:
- Semantic search
- Embeddings
- Vector similarity
- NLP basics
- FastAPI development
- Streamlit applications
- Information retrieval systems

---

# Conclusion

This project demonstrates how modern AI-based search systems work.

Instead of matching exact words, the system searches based on meaning using embeddings and vector similarity.

This is the same core idea used in:
- AI search engines
- recommendation systems
- RAG applications
- intelligent assistants
- modern retrieval systems
