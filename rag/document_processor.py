import os
import google.generativeai as genai
from pypdf import PdfReader
from rag.faiss_store import vector_store

def configure_gemini():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            reader = PdfReader(filepath)
            for page in reader.pages:
                t = page.extract_text()
                if t: text += t + "\n"
        elif ext in ['.txt', '.md']:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        print(f"Error extracting text from {filepath}: {e}")
    return text

def split_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def process_document(filepath, document_id, notebook_id):
    configure_gemini()
    text = extract_text(filepath)
    if not text.strip():
        print(f"No text extracted from {filepath}")
        return False
        
    chunks = split_text(text)
    
    docs = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        if chunk.strip():
            docs.append(chunk)
            metadatas.append({"notebook_id": str(notebook_id), "document_id": str(document_id)})
            ids.append(f"doc_{document_id}_chunk_{i}")
        
    if docs:
        try:
            embeddings = []
            
            for i in range(0, len(docs), 100):
                batch_docs = docs[i:i+100]
                response = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=batch_docs,
                    task_type="retrieval_document"
                )
                embeddings.extend(response['embedding'])
                
            vector_store.add(
                documents=docs,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully embedded {len(docs)} chunks for document {document_id}")
            return True
        except Exception as e:
            print(f"Error embedding document: {e}")
            raise e
            
    return True
