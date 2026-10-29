# 📚 DocuChat — Talk to Any PDF

An AI-powered PDF question-answering application that allows users to upload a PDF document and ask questions about its content using natural language. DocuChat retrieves relevant passages using semantic search and generates answers with the Google Gemini API.

## ✨ Features

- 📄 Upload and process PDF documents.
- 🔍 Extract text from PDFs using PyMuPDF.
- ✂️ Split document text into smaller, overlapping chunks.
- 🧠 Generate semantic embeddings using Sentence Transformers.
- ⚡ Search relevant passages using FAISS.
- 🤖 Generate contextual answers using Google Gemini.
- 📑 Display source passages and PDF page numbers.
- 💬 Ask multiple questions in an interactive Streamlit interface.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web interface |
| PyMuPDF | PDF text extraction |
| Sentence Transformers | Text embeddings |
| FAISS | Similarity search |
| Google Gemini API | AI-generated answers |
| python-dotenv | Environment variable management |
| pytest | Testing |

## 🏗️ How It Works

1. **Upload PDF:** The user uploads a PDF document.
2. **Extract Text:** PyMuPDF extracts selectable text from the document.
3. **Chunk Text:** The extracted content is divided into overlapping chunks.
4. **Create Embeddings:** Sentence Transformers converts text chunks into numerical vectors.
5. **Index Content:** FAISS creates a searchable vector index.
6. **Retrieve Context:** The user's question is matched against relevant document passages.
7. **Generate Answer:** Google Gemini generates an answer based on the retrieved passages.
8. **Show Sources:** The application displays relevant passages and their page numbers.

## 📂 Project Structure

```text
DocuChat/
├── app.py
├── pdf_processor.py
├── chunking.py
├── vector_store.py
├── llm_service.py
├── pyproject.toml
├── .gitignore
├── .env
└── tests/
    └── test_pdf_processor.py
```

**Note:** `.env`, `.venv`, `build/`, and `docuchat.egg-info/` are local environment or generated files. They should not be committed to GitHub. The `.env` file stores your API key and should remain private.

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.11, 3.12, or 3.13
- Git
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/thedhanushdev/DocuChat.git
cd DocuChat
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install .
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Replace the placeholder with your own Gemini API key. Never publish this key or commit the `.env` file.

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

## 🧪 Run Tests

Install pytest if it isn't already installed:

```bash
python -m pip install pytest
```

Run the tests:

```bash
python -m pytest -q
```

## ⚠️ Current Limitations

- The current implementation processes one uploaded PDF at a time.
- Scanned PDFs without selectable text require OCR, which is not currently implemented.
- Answers depend on the relevance of retrieved passages and the availability of the Gemini API.
- The vector index is stored in application memory and is rebuilt when a new PDF is processed.

## 🚀 Future Enhancements

- OCR support for scanned PDFs.
- Chat with multiple PDF documents.
- Persistent vector storage.
- Conversation export and download.
- Improved retrieval and answer evaluation.
- Cloud deployment.

## 🔐 Security

- Keep API keys in environment variables.
- Never commit `.env` or other files containing secrets.
- Do not upload confidential documents to an untrusted deployment.
- Review retrieved document content as untrusted data.

## 👨‍💻 Author

**Dhanush Kannam**

GitHub: [@thedhanushdev](https://github.com/thedhanushdev)

---

*DocuChat — making PDF documents easier to understand through AI.*
