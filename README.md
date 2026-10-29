
# 📄 DocuChat — Talk to Any PDF

**DocuChat** is an AI-powered web application that allows users to upload PDF documents and ask questions about their content using natural language. It retrieves relevant information from the document and generates answers using AI models, with a local fallback when AI services are unavailable.

Built with Python, Streamlit, Sentence Transformers, FAISS, and multiple AI providers.

## 🚀 Features

- 📤 **PDF Upload:** Upload a PDF document and extract its text.
- 💬 **Chat with PDF:** Ask questions about the uploaded document.
- 🔍 **Semantic Search:** Find relevant document passages using vector embeddings.
- 🤖 **Multiple AI Providers:** Supports Groq, OpenAI, and Google Gemini.
- 🔄 **Automatic Fallback:** Tries available AI providers before falling back to local sentence extraction.
- 📚 **Source Exploration:** Explore document content and relevant extracted passages.
- 📊 **Document Overview:** View extracted document information and page details.
- ☁️ **Cloud Deployment:** Deploy the application using Streamlit Community Cloud.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Web interface |
| PyMuPDF | PDF text extraction |
| Sentence Transformers | Text embeddings |
| FAISS | Vector similarity search |
| Groq API | Primary AI answer provider |
| OpenAI API | Secondary AI provider |
| Google Gemini API | Additional AI provider |
| python-dotenv | Local environment variable management |
| Git and GitHub | Version control and source hosting |
| Streamlit Community Cloud | Application deployment |

## 🏗️ Project Architecture

```text
                   ┌──────────────────────┐
                   │        User          │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   Streamlit UI        │
                   │       app.py          │
                   └──────────┬───────────┘
                              │
                    Upload PDF / Ask Question
                              │
                              ▼
                   ┌──────────────────────┐
                   │    PDF Processor      │
                   │   pdf_processor.py    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │    Text Chunking      │
                   │     chunking.py       │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Embeddings and FAISS │
                   │   vector_store.py     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Relevant Text Chunks │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │    LLM Service        │
                   │   llm_service.py      │
                   └──────────┬───────────┘
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
          Groq API        OpenAI API      Gemini API
              └───────────────┼────────────────┘
                              │
                    If AI providers fail
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Local Answer Fallback│
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Answer in Streamlit  │
                   └──────────────────────┘
```

## 📁 Project Structure

```text
DocuChat/
│
├── app.py
├── pdf_processor.py
├── chunking.py
├── vector_store.py
├── llm_service.py
├── requirements.txt
├── pyproject.toml
├── README.md
├── .gitignore
├── .env                  # Local secrets; do not commit
└── tests/
    └── test_pdf_processor.py
```

## ⚙️ How It Works

### 1. Upload a PDF

The user uploads a PDF through the Streamlit interface.

### 2. Extract Text

`pdf_processor.py` uses PyMuPDF to extract selectable text from the PDF, page by page.

### 3. Split Text into Chunks

`chunking.py` divides the extracted text into smaller sections so that relevant information can be retrieved efficiently.

### 4. Generate Embeddings

`vector_store.py` uses the Sentence Transformers model `all-MiniLM-L6-v2` to convert text chunks into numerical vector representations.

### 5. Search Relevant Information

FAISS searches the vector representations to retrieve text chunks related to the user's question.

### 6. Generate an Answer

`llm_service.py` attempts to answer the question using the configured AI providers in this order:

1. Groq
2. OpenAI
3. Google Gemini
4. Local sentence extraction fallback

The answer quality and availability depend on the configured provider, model, API key, and retrieved document content.

## 🧠 Understanding RAG

DocuChat follows a Retrieval-Augmented Generation (RAG) workflow.

RAG combines two processes:

- **Retrieval:** Finds relevant information from the uploaded document.
- **Generation:** Uses an AI model to formulate an answer based on the retrieved information.

This helps the application answer questions about the user's PDF instead of relying only on the AI model's general knowledge.

## 💻 Run Locally on Windows

### Prerequisites

Install the following:

- Python 3.11 or another Python version supported by the project's dependencies
- Git
- Visual Studio Code
- API keys for whichever AI providers you want to use

### Step 1: Clone the Repository

Open PowerShell in VS Code:

```powershell
git clone https://github.com/thedhanushdev/DocuChat.git
cd DocuChat
```

If the project is already on your computer, open its existing folder instead.

### Step 2: Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt or configure the appropriate execution policy for your environment.

### Step 3: Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a file named `.env` in the project root.

Add only the keys and model IDs you have verified for your provider accounts:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_verified_groq_model

OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_verified_openai_model

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_verified_gemini_model
```

Replace the placeholder values with your own credentials. Do not publish this file or commit it to GitHub.

### Step 5: Start the Application

```powershell
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser.

### Step 6: Test the Application

1. Upload a text-based PDF.
2. Wait for processing to finish.
3. Ask a question that can be answered from the document.
4. Review the answer and the available source information.
5. Test the local fallback by temporarily disabling AI credentials in a safe local test environment.

## 🔐 Environment Variables and API Keys

DocuChat supports configuration through environment variables and Streamlit Community Cloud Secrets.

Never store real API keys in source code.

The `.env` file should remain local and be excluded through `.gitignore`. If a key has been exposed, revoke it and create a replacement.

## ☁️ Deploy on Streamlit Community Cloud

### Step 1: Push the Project to GitHub

Make sure the project contains the application files, `requirements.txt`, and the updated `README.md`.

Check your changes:

```powershell
git status
```

Stage and push the required files:

```powershell
git add README.md app.py llm_service.py requirements.txt pyproject.toml .gitignore
git commit -m "Update DocuChat documentation and application"
git push origin main
```

Review staged changes before committing. Never stage or push `.env` or other files containing secrets.

### Step 2: Open Streamlit Community Cloud

Visit:

https://share.streamlit.io/

Sign in using your GitHub account.

### Step 3: Create the App

Select **Create app** and configure:

- **Repository:** `thedhanushdev/DocuChat`
- **Branch:** `main`
- **Main file path:** `app.py`

Choose a Python version supported by your dependencies.

### Step 4: Add Secrets

Open the application's settings and locate the Secrets section.

Use TOML format with your actual replacement API keys and verified model IDs:

```toml
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "your_verified_groq_model"

OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "your_verified_openai_model"

GEMINI_API_KEY = "your_gemini_api_key"
GEMINI_MODEL = "your_verified_gemini_model"
```

Save the settings. Keep these values private.

### Step 5: Deploy and Test

1. Deploy the application.
2. Check the deployment logs if installation fails.
3. Open the deployed URL.
4. Upload a sample PDF.
5. Ask a question and verify that the answer is relevant.
6. Check the logs if AI providers return errors.

A push to the connected GitHub branch normally triggers a redeployment. Changes to Secrets may require the app to restart or rerun.

## 🧩 Important Modules

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI, upload flow, chat, and document views |
| `pdf_processor.py` | PDF loading and text extraction |
| `chunking.py` | Text segmentation |
| `vector_store.py` | Embedding generation and FAISS search |
| `llm_service.py` | AI provider calls and local fallback |
| `requirements.txt` | Python package dependencies |
| `pyproject.toml` | Project metadata and build configuration |
| `tests/` | Automated tests |

## ⚠️ Limitations

- **Scanned PDFs:** The current text-extraction workflow may not read image-only pages because OCR is not yet implemented.
- **Answer accuracy:** AI answers depend on the quality of extracted text, retrieved chunks, and the selected model.
- **Local fallback:** Sentence extraction is a basic fallback, not a full generative AI model.
- **Citations:** Reliable page-level citations depend on preserving page metadata through chunking and retrieval. Verify which citation features are currently implemented in the application.
- **Deployment resources:** Embedding models and FAISS may require additional memory and installation time in the cloud.
- **Provider availability:** API quotas, billing, model availability, and network errors may affect responses.

## 🔮 Future Improvements

- Add OCR support for scanned PDFs using Tesseract or another OCR service.
- Improve page-level citations and show supporting text excerpts.
- Add clickable source-page navigation where supported by the PDF viewer.
- Improve chunking, retrieval ranking, and answer evaluation.
- Add chat history and support for multiple documents.
- Add automated tests for chunking, retrieval, and AI fallback behavior.
- Improve loading indicators, error messages, and deployment diagnostics.
- Add configurable privacy controls and document-processing limits.

## 🧪 Testing

Run the available tests from the project root:

```powershell
python -m pytest
```

If pytest is not installed:

```powershell
pip install pytest
```

## 🔒 Security and Privacy

- Never commit API keys, access tokens, or private credentials.
- Keep `.env` in `.gitignore`.
- Store cloud API keys in Streamlit Secrets.
- Revoke and rotate any credential accidentally exposed.
- Avoid uploading confidential documents unless the deployment's privacy and data-handling requirements are acceptable.
- Apply appropriate limits to document size and processing resources before public deployment.

## 📌 Project Summary

**DocuChat — Talk to Any PDF** demonstrates how PDF text extraction, semantic search, vector databases, and AI language models can be combined to create a document question-answering application.

It is a practical project for exploring Python, Streamlit, embeddings, FAISS, API integration, fallback handling, and cloud deployment.

---

## 📄 License

No license is specified here. Add a `LICENSE` file if you want to publish the project under a particular open-source license.
