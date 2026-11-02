import chromadb
import streamlit as st


@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path="./chroma_db")

    return client.get_or_create_collection(
        name="company_documents",
        metadata={"hnsw:space": "cosine"},
    )


def delete_existing_file_chunks(collection, filename):
    existing = collection.get(where={"filename": filename})

    if existing["ids"]:
        collection.delete(ids=existing["ids"])


def clear_collection(collection):
    existing = collection.get()

    if existing["ids"]:
        collection.delete(ids=existing["ids"])
