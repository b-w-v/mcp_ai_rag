import os, glob, uuid
from dotenv import load_dotenv
from pinecone import Pinecone
from typing import List, Dict

load_dotenv()

INDEX_NAME = os.getenv("PINECONE_INDEX", "netops-rag")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")

# --- Embeddings ---
def embed_texts(texts: List[str]) -> List[List[float]]:
    if EMBEDDING_PROVIDER == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        resp = client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in resp.data]
    else:
        # local (sentence-transformers)
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
        return model.encode(texts, normalize_embeddings=True).tolist()

def chunk(text: str, max_chars=1200) -> List[str]:
    # simple char chunking; Pinecone works fine with this for small labs
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def load_kb_docs(path="knowledge_base/*.md") -> List[Dict]:
    docs = []
    for fp in glob.glob(path):
        with open(fp, "r", encoding="utf-8") as f:
            raw = f.read()
        for i, ch in enumerate(chunk(raw)):
            docs.append({
                "id": f"{os.path.basename(fp)}::{i}::{uuid.uuid4().hex[:8]}",
                "source": os.path.basename(fp),
                "text": ch
            })
    return docs

def ensure_index(pc: Pinecone):
    from pinecone import ServerlessSpec
    dims = 1536 if EMBEDDING_PROVIDER == "openai" else 384  # typical dims
    if INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
        cloud = os.getenv("PINECONE_CLOUD", "aws")
        region = os.getenv("PINECONE_REGION", "us-east-1")
        pc.create_index(
            name=INDEX_NAME, 
            dimension=dims, 
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region)
        )
        print(f"Created new index '{INDEX_NAME}' with dimension {dims}")
    return pc.Index(INDEX_NAME)

def main():
    print("Starting RAG indexing...")
    print(f"Index name: {INDEX_NAME}")
    print(f"Embedding provider: {EMBEDDING_PROVIDER}")
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    print("Connected to Pinecone")
    
    index = ensure_index(pc)
    print(f"Index ready: {INDEX_NAME}")
    
    docs = load_kb_docs()
    print(f"Loaded {len(docs)} document chunks")

    if not docs:
        print("WARNING: No documents found!")
        return

    texts = [d["text"] for d in docs]
    print(f"Generating embeddings for {len(texts)} texts...")
    vecs = embed_texts(texts)
    print(f"Generated {len(vecs)} embeddings")

    to_upsert = []
    for d, v in zip(docs, vecs):
        to_upsert.append({
            "id": d["id"],
            "values": v,
            "metadata": {"source": d["source"]}
        })
    
    print(f"Upserting {len(to_upsert)} vectors...")
    # Pinecone v5 upsert
    index.upsert(vectors=to_upsert, namespace="netops")

    print(f"✅ Upserted {len(to_upsert)} chunks into index '{INDEX_NAME}' (namespace='netops').")

if __name__ == "__main__":
    main()
