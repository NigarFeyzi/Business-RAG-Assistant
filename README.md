# Private AI Document Assistant

A local RAG app: upload PDF or TXT documents and ask questions answered only from their content. Everything runs on your machine using Streamlit, ChromaDB and Ollama.

## Setup

1. Install [Ollama](https://ollama.com) and pull the models:

   ```bash
   ollama pull nomic-embed-text
   ollama pull qwen2.5:1.5b
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

## Usage

Upload documents in the sidebar, click **Process Documents**, then ask questions in the chat. Sources are shown under each answer.

## Project structure

- `app.py` – entry point
- `ui.py` – sidebar, chat and styling
- `documents.py` – text extraction, chunking, indexing
- `rag.py` – retrieval and answer generation
- `database.py` – ChromaDB helpers
