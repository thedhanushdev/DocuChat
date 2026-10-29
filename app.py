
import hashlib

import streamlit as st
from dotenv import load_dotenv

from pdf_processor import extract_pdf_pages
from chunking import split_into_chunks
from vector_store import VectorStore
from llm_service import quick_answer, answer_question

load_dotenv()

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="DocuChat | AI PDF Workspace",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Custom styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .hero {
        padding: 1.5rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #17365D, #365F91);
        color: white;
        margin-bottom: 1.2rem;
    }

    .hero h1 {
        color: white;
        margin-bottom: 0.35rem;
    }

    .hero p {
        color: #E7EFF9;
        margin-bottom: 0;
    }

    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.20);
        padding: 14px;
        border-radius: 12px;
    }

    .status-note {
        padding: 12px;
        border-radius: 10px;
        background: var(--secondary-background-color);
        margin: 8px 0;
    }

    div.stButton > button {
        border-radius: 9px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Session state
# --------------------------------------------------
defaults = {
    "vector_store": None,
    "document_id": None,
    "document_name": None,
    "pages_count": 0,
    "chunks_count": 0,
    "messages": [],
    "questions_asked": 0,
    "latest_sources": [],
    "latest_question": "",
    "latest_answer": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.title("📚 DocuChat")
    st.caption("Your AI-powered PDF workspace")

    st.divider()

    st.subheader("📄 Document")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="Upload a text-based PDF to start asking questions.",
    )

    st.divider()

    st.subheader("⚙️ Answer settings")

    answer_mode = st.radio(
        "Choose answer mode",
        options=["AI answer", "Local answer"],
        index=0,
        help=(
            "AI answer tries Groq, then OpenAI, then Gemini, "
            "and uses local extraction if all providers fail. "
            "Local answer uses no external AI API."
        ),
    )

    if answer_mode == "AI answer":
        st.caption("🤖 Groq → OpenAI → Gemini → Local fallback")
    else:
        st.caption("⚡ Local PDF extraction; no API request")

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.questions_asked = 0
        st.session_state.latest_sources = []
        st.session_state.latest_question = ""
        st.session_state.latest_answer = ""
        st.rerun()

    if st.button("🔄 Reset document", use_container_width=True):
        st.session_state.vector_store = None
        st.session_state.document_id = None
        st.session_state.document_name = None
        st.session_state.pages_count = 0
        st.session_state.chunks_count = 0
        st.session_state.messages = []
        st.session_state.questions_asked = 0
        st.session_state.latest_sources = []
        st.session_state.latest_question = ""
        st.session_state.latest_answer = ""
        st.rerun()

    st.divider()
    st.caption("Built with Streamlit, FAISS and AI APIs.")

# --------------------------------------------------
# Process uploaded PDF
# --------------------------------------------------
if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()
    document_id = hashlib.sha256(pdf_bytes).hexdigest()

    if document_id != st.session_state.document_id:
        try:
            with st.spinner("Reading PDF and building the search index..."):
                pages = extract_pdf_pages(pdf_bytes)

                if not pages:
                    st.error(
                        "No selectable text was found. "
                        "This PDF may need OCR."
                    )
                    st.stop()

                chunks = split_into_chunks(pages)

                if not chunks:
                    st.error("No searchable text chunks were created.")
                    st.stop()

                store = VectorStore()
                store.build(chunks)

            st.session_state.vector_store = store
            st.session_state.document_id = document_id
            st.session_state.document_name = uploaded_file.name
            st.session_state.pages_count = len(pages)
            st.session_state.chunks_count = len(chunks)
            st.session_state.messages = []
            st.session_state.questions_asked = 0
            st.session_state.latest_sources = []
            st.session_state.latest_question = ""
            st.session_state.latest_answer = ""

            st.success("PDF processed successfully!")

        except Exception as exc:
            st.error(f"Could not process PDF: {exc}")
            st.stop()

# --------------------------------------------------
# Hero banner
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>📚 DocuChat</h1>
        <p>Talk to your documents. Find answers. Explore the sources.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Empty state
# --------------------------------------------------
if st.session_state.vector_store is None:
    st.info("👈 Upload a PDF in the sidebar to get started.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📄 Upload")
        st.write("Add a PDF document and prepare it for searching.")

    with col2:
        st.markdown("### 🔎 Ask")
        st.write("Ask questions in natural language.")

    with col3:
        st.markdown("### 💡 Understand")
        st.write("Get answers with relevant PDF source passages.")

    st.stop()

# --------------------------------------------------
# Document header and metrics
# --------------------------------------------------
st.markdown(f"### 📄 {st.session_state.document_name}")

st.caption(
    "Document ready • Search index built • "
    f"Answer mode: {answer_mode}"
)

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "PDF pages",
    st.session_state.pages_count,
)

m2.metric(
    "Searchable chunks",
    st.session_state.chunks_count,
)

m3.metric(
    "Questions asked",
    st.session_state.questions_asked,
)

m4.metric(
    "Chat messages",
    len(st.session_state.messages),
)

st.divider()

# --------------------------------------------------
# Main interactive workspace
# --------------------------------------------------
overview_tab, chat_tab, sources_tab = st.tabs(
    ["📊 Overview", "💬 Chat with PDF", "🔎 Source Explorer"]
)

# --------------------------------------------------
# Overview tab
# --------------------------------------------------
with overview_tab:
    st.subheader("Document overview")

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("#### 📋 Document details")

        st.write(f"**Filename:** {st.session_state.document_name}")
        st.write(f"**Pages processed:** {st.session_state.pages_count}")
        st.write(f"**Searchable chunks:** {st.session_state.chunks_count}")
        st.write(f"**Answer mode:** {answer_mode}")

        st.markdown(
            """
            <div class="status-note">
                <strong>Document status:</strong> Ready for questions
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("#### 🚀 How to get started")

        st.write("1. Open the Chat with PDF tab.")
        st.write("2. Ask a specific question about your document.")
        st.write("3. Review the answer and its source passages.")
        st.write("4. Use Source Explorer to inspect retrieved text.")

        st.info(
            "For better answers, ask one clear question at a time. "
            "AI answers depend on the relevance of the retrieved passages."
        )

    st.markdown("#### 🕘 Recent questions")

    user_questions = [
        message["content"]
        for message in st.session_state.messages
        if message["role"] == "user"
    ]

    if user_questions:
        for number, text in enumerate(reversed(user_questions[-5:]), start=1):
            st.markdown(f"**{number}.** {text}")
    else:
        st.caption("Your questions will appear here after you start chatting.")

# --------------------------------------------------
# Chat tab
# --------------------------------------------------
with chat_tab:
    st.subheader("💬 Ask your PDF")

    st.caption(
        "AI mode uses Groq first, then OpenAI and Gemini. "
        "Local mode avoids external API calls."
    )

    # Display conversation history.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                sources = message.get("sources", [])

                if sources:
                    with st.expander("📄 View source passages"):
                        for source in sources:
                            page = source.get("page", "?")
                            score = source.get("score")

                            if score is not None:
                                st.markdown(
                                    f"**Page {page}** "
                                    f"(similarity: {score:.2f})"
                                )
                            else:
                                st.markdown(f"**Page {page}**")

                            st.write(source.get("text", ""))

    # Suggested prompts.
    st.markdown("#### Try asking")

    prompt_columns = st.columns(3)

    suggestions = [
        "Summarize this document",
        "What are the key points?",
        "What is the main conclusion?",
    ]

    selected_prompt = None

    for index, suggestion in enumerate(suggestions):
        with prompt_columns[index]:
            if st.button(
                suggestion,
                key=f"suggestion_{index}",
                use_container_width=True,
            ):
                selected_prompt = suggestion

    question_input = st.chat_input(
        "Ask a question about your PDF..."
    )

    question = selected_prompt or question_input

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Searching the PDF..."):
                    sources = st.session_state.vector_store.search(
                        question,
                        top_k=4,
                    )

                if answer_mode == "Local answer":
                    with st.spinner("Preparing a local answer..."):
                        answer = quick_answer(question, sources)
                else:
                    with st.spinner("Generating an AI answer..."):
                        answer = answer_question(question, sources)

                st.markdown(answer)

                if sources:
                    with st.expander("📄 View source passages"):
                        for source in sources:
                            page = source.get("page", "?")
                            score = source.get("score")

                            if score is not None:
                                st.markdown(
                                    f"**Page {page}** "
                                    f"(similarity: {score:.2f})"
                                )
                            else:
                                st.markdown(f"**Page {page}**")

                            st.write(source.get("text", ""))

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

                st.session_state.questions_asked += 1
                st.session_state.latest_sources = sources
                st.session_state.latest_question = question
                st.session_state.latest_answer = answer

            except Exception as exc:
                st.error(f"Unable to answer your question: {exc}")

        st.rerun()

# --------------------------------------------------
# Source Explorer tab
# --------------------------------------------------
with sources_tab:
    st.subheader("🔎 Source Explorer")

    st.write(
        "Inspect the passages retrieved for your latest question. "
        "These are the document excerpts used to help generate an answer."
    )

    if st.session_state.latest_question:
        st.markdown(
            f"**Latest question:** {st.session_state.latest_question}"
        )

        if st.session_state.latest_answer:
            with st.expander("View latest answer", expanded=True):
                st.markdown(st.session_state.latest_answer)

        sources = st.session_state.latest_sources

        if sources:
            for index, source in enumerate(sources, start=1):
                page = source.get("page", "?")
                score = source.get("score")

                title = f"Passage {index} — Page {page}"
                if score is not None:
                    title += f" — Similarity {score:.2f}"

                with st.expander(title):
                    st.write(source.get("text", ""))
        else:
            st.warning("No source passages were returned for this question.")

    else:
        st.info(
            "Ask a question in the Chat with PDF tab to explore its sources here."
        )
