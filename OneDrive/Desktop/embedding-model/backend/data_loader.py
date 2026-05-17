import json
import os


def load_documents(path: str = None) -> list:
    """
    Loads documents from JSON file.
    Automatically finds the correct path regardless of
    which folder you run uvicorn from.
    """
    if path is None:
        # os.path.abspath(__file__) = full path to this file
        # dirname twice = goes up two levels to project root
        # Then joins with data/documents.json
        this_file   = os.path.abspath(__file__)
        backend_dir = os.path.dirname(this_file)
        project_dir = os.path.dirname(backend_dir)
        path        = os.path.join(project_dir, "data", "documents.json")

    print(f"Looking for documents at: {path}")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cannot find the required: {path}\n"
            f"Make sure data/documents.json exists in your project root."
        )

    with open(path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"Loaded {len(documents)} documents successfully")
    return documents