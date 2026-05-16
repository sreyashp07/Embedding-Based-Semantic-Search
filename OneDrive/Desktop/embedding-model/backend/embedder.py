from sentence_transformers import SentenceTransformer
import numpy as np

# Lightweight model — 90MB, runs on CPU, no GPU needed
# Downloads once and is cached in: C:/Users/hp/.cache/huggingface/
MODEL_NAME = "all-MiniLM-L6-v2"

print("Loading embedding model: " + MODEL_NAME)
model = SentenceTransformer(MODEL_NAME)
print("Model loaded successfully!")


def get_embedding(text: str) -> np.ndarray:
    """
    Convert one string into a 384-dimensional vector.
    Used for converting the user search query.
    """
    return model.encode(text, convert_to_numpy=True)


def get_embeddings_batch(texts: list) -> np.ndarray:
    """
    Convert a list of strings into vectors all at once.
    Used for indexing all documents at startup. so no hastiness
    Much faster than encoding one by one.
    """
    return model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )