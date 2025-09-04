from typing import List
import os
from pathlib import Path


class Retriever:
    """FAISS/LangChain-ready retrieval facade."""

    def __init__(self):
        self.loaded = False
        self._index = None
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface import HuggingFaceEmbeddings  # ✅ new import

            model_name = os.getenv(
                "EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
            )
            embeddings = HuggingFaceEmbeddings(model_name=model_name)

            index_dir = Path(__file__).resolve().parents[2] / "dataset" / "faiss_index"
            if index_dir.exists():
                self._index = FAISS.load_local(
                    str(index_dir), embeddings, allow_dangerous_deserialization=True
                )
                self.loaded = True
                print(f"✅ FAISS index loaded from {index_dir}")
            else:
                print(f"⚠️ FAISS index not found at {index_dir}")
        except Exception as e:
            print("⚠️ Retriever init failed:", e)
            self.loaded = False

    def search(self, query: str, k: int = 3) -> List[str]:
        if self.loaded and self._index is not None:
            try:
                docs = self._index.similarity_search(query, k=k)
                return [d.page_content for d in docs]
            except Exception as e:
                print("⚠️ FAISS search failed:", e)

        # Fallback placeholder
        return [
            "General hydration and rest advice.",
            "Consult a healthcare professional for persistent symptoms.",
        ]
