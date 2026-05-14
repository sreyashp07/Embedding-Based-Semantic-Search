import json
import os


def load_documents(path: str = "data/documents.json") -> list:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cannot find documents file at: '{path}'\n"
            f"Make sure data/documents.json exists."
        )
    with open(path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    print(f"Loaded {len(documents)} documents from {path}")
    return documents