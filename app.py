import streamlit as st

st.set_page_config(
    page_title="Private AI Document Assistant",
    page_icon="📚",
    layout="wide",
)

from database import get_collection  # noqa: E402
from ui import (  # noqa: E402
    apply_styles,
    handle_question,
    render_chat_history,
    render_header,
    render_sidebar,
    render_status,
)

apply_styles()
render_header()

collection = get_collection()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

if "last_processed_at" not in st.session_state:
    st.session_state.last_processed_at = None

render_sidebar(collection)
render_status(collection)
render_chat_history()

question = st.chat_input("Ask a question about your documents...")

if question:
    handle_question(collection, question)
