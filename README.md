<div align="center">
  <img src="https://img.icons8.com/clouds/200/000000/brain.png" alt="Logo" width="150" height="150">

  # Advanced AI Research Assistant 🚀

  <p>
    <strong>A powerful, intelligent workspace that combines document notes with an autonomous, web-connected research agent.</strong>
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

The **Advanced AI Research Assistant** transforms traditional note-taking into an autonomous intelligence hub. Powered by LangGraph and Google Generative AI (Gemini), the platform offers a powerful dual-model system: you can use the **Local RAG Chatbot** to strictly query your private uploaded documents, or engage the **Autonomous Agent** to perform live web searches, scrape web pages, and automatically dispatch comprehensive executive reports via email.

## ✨ Key Features

| Feature | Description |
| ------- | ----------- |
| 🔍 **Autonomous Web Searching** | The agent dynamically breaks down your research topics and queries the open web (DuckDuckGo Search) to gather up-to-date intel. |
| 🕸️ **Deep Web Scraping** | Uses web scraping to extract full text context from URLs, incorporating detailed external content directly into your reports. |
| 📧 **Automated Email Reports** | Generates highly structured, executive summaries and automatically emails the final research report directly to your inbox. |
| 📄 **Document Processing & RAG** | Upload PDFs and text directly into project "Notebooks." The system automatically embeds and indexes them for high-speed semantic search. |
| 💬 **Conversational RAG Chatbot** | A dedicated, local chat interface that answers questions strictly using your uploaded documents, ensuring responses are grounded directly in your private context via FAISS. |
| 🤖 **Advanced LangGraph Agent** | A floating, smart conversational assistant capable of routing between local document tools and web tools seamlessly. |
| 📝 **Strict Plain-Text Outputs** | The agent interface ensures distraction-free, pure plain-text output, natively removing markdown for streamlined readability. |
| 📓 **Intelligent Notebook Management** | Create distinct notebooks to elegantly organize personal documents, securely compartmentalized by user authentication. |
| 🧹 **Resource Cleanup** | Safe, automated removal of related files and vector embeddings to keep your storage clean when a notebook is deleted. |

## 🛠️ Technology Stack

Our platform leverages a robust and modern stack:

*   **Backend Engineering:** Python 3, Flask, Werkzeug
*   **AI & Orchestration:** LangChain, LangGraph, Google Generative AI (Gemini SDK)
*   **Vector Database (RAG):** FAISS / ChromaDB for ultra-fast similarity search
*   **Web Toolkit:** DuckDuckGo Search API, Requests, BeautifulSoup4
*   **Communication:** SMTP Email Integration
*   **Database:** SQLite for user and metadata management
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
   # Core Config
   FLASK_SECRET_KEY="your_super_secret_key"
   
   # AI Config
   GOOGLE_API_KEY="your_google_gemini_api_key"
   
   # Email Config (for Report Dispatch)
   SMTP_SERVER="smtp.gmail.com"
   SMTP_PORT="587"
   EMAIL_USER="your_email@gmail.com"
   EMAIL_PASSWORD="your_app_password"
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
├── .env                   # Environment variables (API keys, secrets, SMTP)
├── database/              # Relational database models and initialization
├── rag/                   # AI logic, document processing, and RAG pipelines
│   ├── document_processor.py # Parses and chunks files
│   ├── faiss_store.py     # Vector database initialization and queries
│   ├── tools.py           # Web search, scraping, file ops, and email tools
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
