import os
import uuid
from datetime import datetime, timezone

from pinecone import Pinecone
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.environ["pinecone_api"]
PINECONE_INDEX_NAME = "jarvis-memory"


pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(PINECONE_INDEX_NAME)


embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


def create_memory(
    user_id: str,
    content: str,
    category: str,
    importance: int
):

    memory_id = str(uuid.uuid4())

    vector = embeddings.embed_query(content)

    now = datetime.now(timezone.utc).isoformat()

    index.upsert(
        namespace=user_id,
        vectors=[
            {
                "id": memory_id,
                "values": vector,
                "metadata": {
                    "content": content,
                    "category": category,
                    "importance": importance,
                    "created_at": now,
                    "updated_at": now,
                }
            }
        ]
    )

    return memory_id


def search_memories(
    user_id: str,
    query: str,
    top_k: int = 5
):

    query_vector = embeddings.embed_query(query)
    results = index.query(
        namespace=user_id,
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    memories = []

    for match in results.matches:

        memories.append({
            "id": match.id,
            "score": match.score,
            "content": match.metadata.get("content"),
            "category": match.metadata.get("category"),
            "importance": match.metadata.get("importance"),
        })

    return memories


def update_memory(
    user_id: str,
    memory_id: str,
    content: str,
    category: str,
    importance: int
):

    vector = embeddings.embed_query(content)

    now = datetime.now(timezone.utc).isoformat()

    index.upsert(
        namespace=user_id,
        vectors=[
            {
                "id": memory_id,
                "values": vector,
                "metadata": {
                    "content": content,
                    "category": category,
                    "importance": importance,
                    "updated_at": now,
                }
            }
        ]
    )

def delete_memory(
    user_id: str,
    memory_id: str
):

    index.delete(
        namespace=user_id,
        ids=[memory_id]
    )

# from pinecone import Pinecone, ServerlessSpec


# if not pc.has_index(PINECONE_INDEX_NAME):

#     pc.create_index(
#         name=PINECONE_INDEX_NAME,
#         dimension=768,
#         metric="cosine",
#         spec=ServerlessSpec(
#             cloud="aws",
#             region="us-east-1"
#         )
#     )


