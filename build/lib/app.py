
import streamlit as st
from dotenv import load_dotenv

from pdf_processor import extract_pdf_pages
from chunking import split_into_chunks
from vector_store import VectorStore
from llm_service import answer_question

load_dotenv()

st.set_page_config(
    page_title="DocuChat",
    page_icon="📚",
    layout="wide"
)

st.title("📚 DocuChat: Talk to Any PDF")
st.caption("Upload a PDF and ask questions about its contents.")

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "document_name" not in st.session_state:
    st.session_state.document_name = None

if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()
    document_id = (
        uploaded_file.name,
        len(pdf_bytes),
        hash(pdf_bytes)
    )

    if document_id != st.session_state.document_id:
        try:
            with st.spinner("Processing PDF and building search index..."):
                pages = extract_pdf_pages(pdf_bytes)

                if not pages:
                    st.error(
                        "No selectable text found. "
                        "This PDF may require OCR."
                    )
                    st.stop()

                chunks = split_into_chunks(pages)

                store = VectorStore()
                store.build(chunks)

                st.session_state.vector_store = store
                st.session_state.document_id = document_id
                st.session_state.document_name = uploaded_file.name
                st.session_state.messages = []

            st.success(
                f"Processed {len(pages)} text pages "
                f"into {len(chunks)} chunks."
            )

        except Exception as exc:
            st.error(f"Could not process PDF: {exc}")
            st.stop()

if st.session_state.vector_store is not None:
    st.subheader(
        f"Chatting with: {st.session_state.document_name}"
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("Source passages"):
                    for source in message["sources"]:
                        st.markdown(
                            f"**Page {source['page']}** "
                            f"(similarity: {source['score']:.2f})"
                        )
                        st.write(source["text"])

    question = st.chat_input("Ask a question about your PDF")

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Finding relevant passages and answering..."):
                    sources = st.session_state.vector_store.search(
                        question
                    )
                    answer = answer_question(question, sources)

                st.markdown(answer)

                with st.expander("Source passages"):
                    for source in sources:
                        st.markdown(
                            f"**Page {source['page']}** "
                            f"(similarity: {source['score']:.2f})"
                        )
                        st.write(source["text"])

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except Exception as exc:
                st.error(f"Unable to answer: {exc}")

else:
    st.info("Upload a PDF to start chatting.")
