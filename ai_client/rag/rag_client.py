import os
from typing import List, Tuple
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
INDEX_NAME = os.getenv("PINECONE_INDEX", "netops-rag")
NAMESPACE = "netops"
TOP_K = 5

def embed_query(text: str) -> List[float]:
    provider = os.getenv("EMBEDDING_PROVIDER", "openai")
    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        return client.embeddings.create(model=model, input=[text]).data[0].embedding
    else:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
        return model.encode([text], normalize_embeddings=True)[0].tolist()

def retrieve(query: str, top_k: int = TOP_K) -> List[Tuple[str, float, str]]:
    """
    Retrieve relevant documents from Pinecone based on query.
    Returns: List of (document_id, score, source)
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    idx = pc.Index(INDEX_NAME)
    qv = embed_query(query)
    res = idx.query(vector=qv, top_k=top_k, include_metadata=True, namespace=NAMESPACE)
    
    hits = []
    for m in res.get("matches", []):
        doc_id = m["id"]
        score = m.get("score", 0.0)
        source = m["metadata"].get("source", "unknown")
        hits.append((doc_id, score, source))
    
    return hits

def retrieve_with_context(query: str, top_k: int = TOP_K) -> str:
    """
    Retrieve relevant documents and format them as context for LLM.
    """
    hits = retrieve(query, top_k)
    
    if not hits:
        return "No relevant documentation found."
    
    context_parts = []
    context_parts.append(f"Found {len(hits)} relevant knowledge base entries:\n")
    
    for i, (doc_id, score, source) in enumerate(hits, 1):
        context_parts.append(f"{i}. Source: {source} (relevance: {score:.2f})")
        context_parts.append(f"   Document ID: {doc_id}\n")
    
    return "\n".join(context_parts)
