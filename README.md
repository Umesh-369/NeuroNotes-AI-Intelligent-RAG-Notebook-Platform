<div align="center">
  <img src="https://img.icons8.com/clouds/200/000000/brain.png" alt="Logo" width="150" height="150">

  # GenAI Notebook Platform 🚀

  <p>
    <strong>A powerful, intelligent workspace that combines traditional note-taking with cutting-edge Generative AI.</strong>
  </p>

  <!-- Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg" alt="Flask" />
    <img src="https://img.shields.io/badge/AI-LangChain%20%7C%20LangGraph-orange.svg" alt="AI Stack" />
    <img src="https://img.shields.io/badge/VectorDB-FAISS%20%7C%20ChromaDB-green.svg" alt="Database" />
    <img src="https://img.shields.io/badge/License-MIT-success.svg" alt="License" />
  </p>
</div>

---

## 📖 Overview

The **GenAI Notebook Platform** empowers users to create smart notebooks, upload reference documents, and interact seamlessly with their data. Powered by Retrieval-Augmented Generation (RAG) and intelligent LangGraph-powered AI agents, this platform acts as your personal AI research assistant.

## ✨ Key Features

| Feature | Description |
| ------- | ----------- |
| 🔐 **Secure User Authentication** | Full signup, login, and session management system to keep your personal notebooks strictly private and secure. |
| 📓 **Intelligent Notebooks** | Create and manage distinct notebooks to elegantly organize your thoughts, projects, and related documents. |
| 📄 **Document Processing & RAG** | Upload PDFs and text directly into notebooks. The system automates extraction, embedding, and indexing for instantaneous semantic search. |
| 💬 **Conversational Querying** | A dedicated interface for chatting with your documents, producing dynamic and grounded responses backed by accurate source citations. |
| 🤖 **Floating AI Agent** | A smart, independent floating chat assistant powered by LangGraph and Google Generative AI, accessible from anywhere. |
| 💡 **Insights Management** | Save AI-generated answers or personal notes as "Insights" within your notebook for quick future reference. |
| 🧹 **Resource Cleanup** | Fully managed resource deletion safely removes related files and vector embeddings to keep your storage clean when a notebook is deleted. |

## 🛠️ Technology Stack

Our platform leverages a robust and modern stack:

*   **Backend Engineering:** Python 3, Flask, Werkzeug
*   **AI & Orchestration:** LangChain, LangGraph, Google Generative AI (Gemini SDK)
*   **Vector Database (RAG):** FAISS / ChromaDB for ultra-fast similarity search
*   **Document Parsing:** PyPDF
*   **Database:** Local Relational Database (SQLite) for comprehensive metadata management
*   **Frontend Design:** HTML5, CSS3, Vanilla JavaScript, Jinja2 Templates

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Ensure you have the following installed:
*   Python 3.8 or higher
*   [Google Gemini API Key](https://aistudio.google.com/)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd GenAI
   ```

2. **Set up the virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory and add your secret keys:
   ```env
   FLASK_SECRET_KEY="your_super_secret_key"
   GOOGLE_API_KEY="your_google_gemini_api_key"
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   > 🌐 The application will be accessible at `http://localhost:5000`.

## 📂 Project Structure

A quick look at the top-level files and directories you'll see in this project:

```text
GenAI/
├── app.py                 # Main Flask application and API routing
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables (API keys, secrets)
├── database/              # Relational database models and initialization
├── rag/                   # AI logic, document processing, and RAG pipelines
│   ├── document_processor.py # Parses and chunks files
│   ├── faiss_store.py     # Vector database initialization and queries
│   ├── chatbot.py         # Standard RAG retrieval logic
│   └── agent.py           # LangGraph-based conversational agent
├── templates/             # Jinja2 HTML templates
├── static/                # Static assets (CSS, JS, Images)
└── uploads/               # Local directory for uploaded user documents
```

## 🤝 Contributing

Contributions, issues, and feature requests are always welcome! <br>
Feel free to check out the [issues page](#) to report bugs or suggest enhancements.

## 📝 License

This project is generously licensed under the **MIT License**.
