"""
Build a FAISS index from dataset/*.txt

Usage:
  python backend/scripts/index_faiss.py
"""

import glob
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def main():
    dataset_dir = Path(__file__).resolve().parents[2] / "dataset"
    out_dir = dataset_dir / "faiss_index"
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_files = list(glob.glob(str(dataset_dir / "*.txt")))
    if not txt_files:
        print("No dataset/*.txt found. Add healthcare texts first.")
        return

    raw_docs = []
    for fp in txt_files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                raw_docs.append(f.read())
        except Exception as e:
            print("Error reading file:", fp, e)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = []
    for doc in raw_docs:
        chunks.extend(splitter.split_text(doc))

    model_name = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vs = FAISS.from_texts(chunks, embedding=embeddings)
    vs.save_local(str(out_dir))
    print("✅ Saved FAISS index to:", out_dir)


if __name__ == "__main__":
    main()
