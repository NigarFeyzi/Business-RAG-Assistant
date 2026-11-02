import uuid

import ollama
import pymupdf

from database import delete_existing_file_chunks


# Text extraction
def extract_pdf(uploaded_file):
    pdf_bytes = uploaded_file.getvalue()

    document = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text()

        if text.strip():
            pages.append(
                {
                    "text": text,
                    "page": page_number + 1,
                    "filename": uploaded_file.name,
                }
            )

    document.close()

    return pages


def extract_txt(uploaded_file):
    raw_bytes = uploaded_file.getvalue()

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1")

    return [
        {
            "text": text,
            "page": 1,
            "filename": uploaded_file.name,
        }
    ]


# Chunking
def chunk_text(text, chunk_size=1200, overlap=200):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# Process documents
def process_documents(collection, files):
    processed_summary = []

    for uploaded_file in files:
        filename = uploaded_file.name

        # Prevent duplicate chunks if same file is processed again
        delete_existing_file_chunks(collection, filename)

        if filename.lower().endswith(".pdf"):
            pages = extract_pdf(uploaded_file)

        elif filename.lower().endswith(".txt"):
            pages = extract_txt(uploaded_file)

        else:
            continue

        total_chunks = 0

        for page_data in pages:
            chunks = chunk_text(page_data["text"])

            for chunk_index, chunk in enumerate(chunks):
                embedding_response = ollama.embed(
                    model="nomic-embed-text",
                    input=chunk,
                )

                embedding = embedding_response["embeddings"][0]

                collection.add(
                    ids=[str(uuid.uuid4())],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[
                        {
                            "filename": filename,
                            "page": page_data["page"],
                            "chunk": chunk_index,
                        }
                    ],
                )

                total_chunks += 1

        processed_summary.append(
            {
                "filename": filename,
                "pages": len(pages),
                "chunks": total_chunks,
            }
        )

    return processed_summary
