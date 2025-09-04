from typing import List


class Retriever:
    """Interface for retrieval (e.g., FAISS/Vector DB).

    Implement index creation, embedding, and similarity search later.
    """

    def __init__(self):
        pass

    def search(self, query: str, k: int = 3) -> List[str]:
        _ = (query, k)
        # Placeholder results
        return [
            "General hydration and rest guidance from public health sources.",
            "When to seek medical attention for persistent symptoms.",
        ]


