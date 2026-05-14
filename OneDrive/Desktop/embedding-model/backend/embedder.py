from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"

print(f"Loading model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)
print("Model loaded!")


def get_embedding(text: str) -> np.ndarray:
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding


def get_embeddings_batch(texts: list) -> np.ndarray:
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    return embeddings