from datetime import datetime

import streamlit as st

from database import clear_collection
from documents import process_documents
from rag import generate_answer, retrieve_context


# Styling and header
def apply_styles():
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
                max-width: 1200px;
            }

            .main-title {
                font-size: 2.4rem;
                font-weight: 700;
                margin-bottom: 0.3rem;
            }

            .subtitle {
                color: #6b7280;
                font-size: 1rem;
                margin-bottom: 1.5rem;
            }

            .status-box {
                padding: 0.8rem 1rem;
                border-radius: 12px;
                background: #f3f4f6;
                margin-bottom: 1rem;
            }

            .source-card {
                padding: 0.7rem 0.9rem;
                border-radius: 10px;
                border: 1px solid #e5e7eb;
                margin-bottom: 0.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        '<div class="main-title">📚 Private AI Document Assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="subtitle">
            Upload company documents and ask questions using only the information inside them.
        </div>
        """,
        unsafe_allow_html=True,
    )


# Sidebar
def render_sidebar(collection):
    with st.sidebar:
        st.header("Knowledge Base")

        st.caption("Upload PDF or TXT documents.")

        uploaded_files = st.file_uploader(
            "Documents",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        process_button = st.button(
            "Process Documents",
            type="primary",
            use_container_width=True,
        )

        if process_button:
            if not uploaded_files:
                st.warning("Please upload at least one document.")
            else:
                progress_placeholder = st.empty()

                with st.spinner("Reading and indexing documents..."):
                    summary = process_documents(collection, uploaded_files)

                st.session_state.processed_files = summary
                st.session_state.last_processed_at = datetime.now().strftime("%H:%M")

                progress_placeholder.success("Documents processed successfully.")

        st.divider()

        st.subheader("Status")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Chunks", collection.count())

        with col2:
            st.metric("Files", len(st.session_state.processed_files))

        if st.session_state.last_processed_at:
            st.caption(f"Last processed: {st.session_state.last_processed_at}")

        if st.session_state.processed_files:
            st.divider()

            st.subheader("Processed Documents")

            for file_info in st.session_state.processed_files:
                st.markdown(
                    f"""
                    **📄 {file_info['filename']}**

                    Pages: {file_info['pages']}  
                    Chunks: {file_info['chunks']}
                    """
                )

        st.divider()

        if st.button("Clear Knowledge Base", use_container_width=True):
            clear_collection(collection)

            st.session_state.messages = []
            st.session_state.processed_files = []
            st.session_state.last_processed_at = None

            st.success("Knowledge base cleared.")
            st.rerun()


# Main content
def render_status(collection):
    if collection.count() == 0:
        st.info(
            "Upload and process documents from the sidebar to start asking questions."
        )
    else:
        st.success(
            f"Knowledge base ready — {collection.count()} document chunks indexed."
        )


def render_sources(sources):
    with st.expander("View sources"):
        for source in sources:
            st.markdown(
                f"""
                <div class="source-card">
                    📄 <b>{source['filename']}</b><br>
                    Page {source['page']}
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                render_sources(message["sources"])


def handle_question(collection, question):
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    if collection.count() == 0:
        answer = "Please upload and process documents first."

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

    else:
        with st.chat_message("assistant"):
            with st.spinner("Searching your documents..."):
                results = retrieve_context(collection, question)
                answer, sources = generate_answer(question, results)

            st.markdown(answer)

            if sources:
                render_sources(sources)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
