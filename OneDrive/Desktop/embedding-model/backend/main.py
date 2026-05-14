from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from embedder import get_embedding, get_embeddings_batch
from search_engine import search_engine
from data_loader import load_documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting server...")
    loaded = search_engine.load_index()
    if not loaded:
        print("No index found. Creating now...")
        try:
            documents  = load_documents()
            texts      = [doc["content"] for doc in documents]
            embeddings = get_embeddings_batch(texts)
            search_engine.index_documents(documents, embeddings)
        except FileNotFoundError as e:
            print(f"Warning: {e}")
    yield
    print("Server shutting down...")


app = FastAPI(
    title="Semantic Search API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class IndexRequest(BaseModel):
    data_path: str = "data/documents.json"


@app.get("/")
def root():
    return {
        "message": "Semantic Search API is running!",
        "docs":    "http://localhost:8000/docs",
        "status":  "healthy"
    }


@app.get("/status")
def get_status():
    indexed = search_engine.embeddings is not None
    return {
        "indexed":        indexed,
        "document_count": len(search_engine.documents) if indexed else 0,
        "model":          "all-MiniLM-L6-v2"
    }


@app.post("/index")
def index_documents(request: IndexRequest = IndexRequest()):
    try:
        documents  = load_documents(request.data_path)
        texts      = [doc["content"] for doc in documents]
        embeddings = get_embeddings_batch(texts)
        search_engine.index_documents(documents, embeddings)
        return {
            "success":        True,
            "message":        f"Indexed {len(documents)} documents",
            "document_count": len(documents)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
def search(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if search_engine.embeddings is None:
        raise HTTPException(status_code=503, detail="No documents indexed yet.")
    query_embedding = get_embedding(request.query)
    results = search_engine.search(query_embedding, top_k=request.top_k)
    return {
        "query":         request.query,
        "total_results": len(results),
        "results":       results
    }


@app.get("/documents")
def list_documents():
    if not search_engine.documents:
        return {"documents": [], "count": 0}
    return {
        "documents": search_engine.documents,
        "count":     len(search_engine.documents)
    }