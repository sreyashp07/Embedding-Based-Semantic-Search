import numpy as np
import json
import os
from sklearn.metrics.pairwise import cosine_similarity

EMBEDDINGS_PATH = "embeddings/index.npy"
DOCUMENTS_PATH  = "embeddings/documents.json"


class SearchEngine:

    def __init__(self):
        self.embeddings = None
        self.documents  = []

    def index_documents(self, documents: list, embeddings: np.ndarray):
        self.documents  = documents
        self.embeddings = embeddings
        os.makedirs("embeddings", exist_ok=True)
        np.save(EMBEDDINGS_PATH, embeddings)
        with open(DOCUMENTS_PATH, "w") as f:
            json.dump(documents, f, indent=2)
        print(f"Indexed {len(documents)} documents successfully")

    def load_index(self) -> bool:
        if not os.path.exists(EMBEDDINGS_PATH) or \
           not os.path.exists(DOCUMENTS_PATH):
            return False
        self.embeddings = np.load(EMBEDDINGS_PATH)
        with open(DOCUMENTS_PATH, "r") as f:
            self.documents = json.load(f)
        print(f"Loaded index: {len(self.documents)} documents")
        return True

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list:
        if self.embeddings is None or len(self.documents) == 0:
            return []
        query_vec  = query_embedding.reshape(1, -1)
        scores     = cosine_similarity(query_vec, self.embeddings)[0]
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


search_engine = SearchEngine()