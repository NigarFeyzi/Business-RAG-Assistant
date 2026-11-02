import ollama


# Retrieval
def retrieve_context(collection, question, n_results=5):
    embedding_response = ollama.embed(
        model="nomic-embed-text",
        input=question,
    )

    question_embedding = embedding_response["embeddings"][0]

    available_chunks = collection.count()

    safe_n_results = min(n_results, available_chunks)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=safe_n_results,
    )

    return results


# Source formatting
def build_unique_sources(metadatas):
    unique_sources = []

    seen = set()

    for source in metadatas:
        key = (source["filename"], source["page"])

        if key not in seen:
            seen.add(key)

            unique_sources.append(
                {
                    "filename": source["filename"],
                    "page": source["page"],
                }
            )

    return unique_sources


# Answer generation
def generate_answer(question, results):
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return (
            "I could not find this information in the uploaded documents.",
            [],
        )

    context_parts = []

    for document, metadata in zip(documents, metadatas):
        context_parts.append(
            f"""
File: {metadata['filename']}
Page: {metadata['page']}

{document}
"""
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
You are a private company document assistant.

Answer the user's question ONLY using the provided context.

Rules:
1. Do not use outside knowledge.
2. Do not invent information.
3. If the answer is not clearly available in the context, respond exactly:
   I could not find this information in the uploaded documents.
4. Keep the answer concise and professional.

CONTEXT:

{context}

QUESTION:

{question}
"""

    response = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response["message"]["content"].strip()

    not_found = "I could not find this information in the uploaded documents."

    if not_found.lower() in answer.lower():
        return not_found, []

    # Show only the most relevant retrieved source
    top_source = metadatas[0]

    sources = [
        {
            "filename": top_source["filename"],
            "page": top_source["page"],
        }
    ]

    return answer, sources
