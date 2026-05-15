import numpy as np
import json
import os
from sklearn.metrics.pairwise import cosine_similarity


# Automatically find project root folder
# This file is at: project/backend/search_engine.py
# So dirname twice gets us to: project/
THIS_FILE   = os.path.abspath(__file__)
BACKEND_DIR = os.path.dirname(THIS_FILE)
PROJECT_DIR = os.path.dirname(BACKEND_DIR)

# Embedding files will be saved here: project/embeddings/
EMBEDDINGS_PATH = os.path.join(PROJECT_DIR, "embeddings", "index.npy")
DOCUMENTS_PATH  = os.path.join(PROJECT_DIR, "embeddings", "documents.json")
EMBEDDINGS_DIR  = os.path.join(PROJECT_DIR, "embeddings")


class SearchEngine:
    """
    Manages document embeddings and performs cosine similarity search.
    """

    def __init__(self):
        self.embeddings = None   # numpy array shape (N, 384)
        self.documents  = []     # list of document dicts


    def index_documents(self, documents: list, embeddings: np.ndarray):
        """
        Save documents and embeddings to memory and disk.
        Called once at startup or when re-indexing.
        """
        self.documents  = documents
        self.embeddings = embeddings

        # Create embeddings folder if it does not exist
        os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

        # Save embeddings as binary numpy file (fast to reload)
        np.save(EMBEDDINGS_PATH, embeddings)

        # Save documents as JSON
        with open(DOCUMENTS_PATH, "w") as f:
            json.dump(documents, f, indent=2)

        print(f"Indexed {len(documents)} documents successfully")
        print(f"Saved to: {EMBEDDINGS_PATH}")


    def load_index(self) -> bool:
        """
        Load previously saved embeddings from disk.
        Returns True if loaded, False if no saved index found.
        """
        if not os.path.exists(EMBEDDINGS_PATH):
            print("No saved embeddings found at: " + EMBEDDINGS_PATH)
            return False

        if not os.path.exists(DOCUMENTS_PATH):
            print("No saved documents found at: " + DOCUMENTS_PATH)
            return False

        self.embeddings = np.load(EMBEDDINGS_PATH)

        with open(DOCUMENTS_PATH, "r") as f:
            self.documents = json.load(f)

        print(f"Loaded existing index: {len(self.documents)} documents")
        return True


    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list:
        """
        Find top_k most similar documents to the query.

        Steps:
        1. Reshape query to 2D array for sklearn
        2. Compute cosine similarity vs all documents
        3. Sort by score descending
        4. Return top_k results
        """
        if self.embeddings is None or len(self.documents) == 0:
            return []

        # Reshape from (384,) to (1, 384) — sklearn needs 2D
        query_vec = query_embedding.reshape(1, -1)

        # Compare query against ALL document vectors at once
        # scores shape: (N,) — one score per document
        scores = cosine_similarity(query_vec, self.embeddings)[0]

        # Sort indices highest score first, take top_k
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc = self.documents[idx]
            results.append({
                "id":      doc["id"],
                "title":   doc["title"],
                "content": doc["content"],
                "score":   float(round(scores[idx], 4))
            })

        return results


# Single global instance — loaded once, reused for every search request
search_engine = SearchEngine()