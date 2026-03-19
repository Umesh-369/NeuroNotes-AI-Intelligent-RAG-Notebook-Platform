import os
from langchain_core.tools import tool
from rag.faiss_store import vector_store
from database.models import get_document_by_id, get_notebook_documents, add_document
from rag.document_processor import extract_text, process_document
from rag.faiss_store import vector_store
from rag.document_editor import extract_images_to_pdf, edit_pdf_pages
import google.generativeai as genai

@tool
def search_knowledge_base(query: str, notebook_id: int, document_id: int = None) -> str:
    """
    Search the notebook's uploaded documents for the given query using semantic search.
    Returns relevant text snippets. Use this to answer general questions about the documents.
    """
    try:
        if not os.environ.get("GOOGLE_API_KEY"):
            return "Error: GOOGLE_API_KEY is not set."
            
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = response['embedding']
        
        where_filter = {"notebook_id": str(notebook_id)}
        if document_id:
            where_filter["document_id"] = str(document_id)
            
        results = vector_store.query(
            query_embeddings=[query_embedding],
            n_results=5,
            where=where_filter
        )
        context_chunks = results['documents'][0] if (results and 'documents' in results and results['documents']) else []
        if not context_chunks:
            return "No relevant information found in the documents."
        return "\n...\n".join(context_chunks)
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

@tool
def read_full_document(document_id: int) -> str:
    """
    Read the entire text content of a specific document by its document ID.
    Useful when you need the exact full context to rewrite, restructure, or summarize an entire file.
    """
    doc = get_document_by_id(document_id)
    if not doc:
        return f"Error: Document with ID {document_id} not found."
    text = extract_text(doc['filepath'])
    # Return up to 30000 characters to prevent massive context overflow in extreme cases
    return text[:30000]

@tool
def list_notebook_documents(notebook_id: int) -> str:
    """
    List all documents currently available in the user's notebook.
    Returns a list of document IDs and filenames so you know which IDs to reference.
    """
    docs = get_notebook_documents(notebook_id)
    if not docs:
        return "No documents found in this notebook."
    
    result = "Documents in notebook:\n"
    for d in docs:
        result += f"- Document ID: {d['id']}, Filename: {d['filename']}\n"
    return result

@tool
def create_derived_document(notebook_id: int, title: str, content: str) -> str:
    """
    Create a new document file in the notebook with the specified title and text content.
    Use this when the user asks you to "create", "generate", "extract to a new file", or "save" a document.
    The title should ideally include a .txt extension (e.g., 'summary.txt').
    """
    if not title.endswith('.txt') and not title.endswith('.md'):
        title += '.txt'
        
    # Get the precise path to the uploads folder relative to the root
    # rag/tools.py -> Project/GenAI/uploads
    root_dir = os.path.dirname(os.path.dirname(__file__))
    upload_folder = os.path.join(root_dir, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    import re
    safe_title = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', title)
    filepath = os.path.join(upload_folder, f"derived_{notebook_id}_{safe_title}")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        doc_id = add_document(notebook_id, safe_title, filepath)
        process_success = process_document(filepath, doc_id, notebook_id)
        
        if process_success:
            return f"Success! Created new document '{safe_title}' (ID {doc_id}). The user will now see this file in their dashboard."
        else:
            return f"Created document '{safe_title}' (ID {doc_id}), but failed to embed it for semantic search."
    except Exception as e:
        return f"Error creating document: {str(e)}"

@tool
def extract_images_from_document(document_id: int, notebook_id: int) -> str:
    """
    Extracts all images from a PDF document and places them into a newly created PDF document.
    Use this when a user asks to "extract images" or "save images" from a PDF.
    """
    doc = get_document_by_id(document_id)
    if not doc:
        return f"Error: Document with ID {document_id} not found."
        
    try:
        from rag.document_editor import extract_images_to_pdf
        filepath, new_filename = extract_images_to_pdf(document_id, notebook_id, doc['filepath'])
        if not filepath:
            return "No images were found in the document to extract."
            
        new_doc_id = add_document(notebook_id, new_filename, filepath)
        process_success = process_document(filepath, new_doc_id, notebook_id)
        
        status = "and is ready for use." if process_success else "but semantic indexing failed."
        return f"Successfully extracted images to a new document '{new_filename}' (ID {new_doc_id}) {status}"
    except Exception as e:
        return f"Error extracting images: {str(e)}"

@tool
def remove_pages_from_document(document_id: int, notebook_id: int, remove_pages: list[int], overwrite: bool = False) -> str:
    """
    Removes specific pages from a PDF document.
    `remove_pages` should be a list of 1-based integers (e.g., [3] for page 3, [1, 5] for pages 1 and 5).
    If `overwrite` is True, it will modify the existing document permanently.
    If `overwrite` is False, it will save the modified version as a new document.
    """
    doc = get_document_by_id(document_id)
    if not doc:
        return f"Error: Document with ID {document_id} not found."
        
    try:
        from rag.document_editor import edit_pdf_pages
        filepath, new_filename = edit_pdf_pages(document_id, notebook_id, doc['filepath'], remove_pages, overwrite=overwrite)
        
        if overwrite:
            # Document modified in place. Need to wipe old embeddings and recreate them.
            vector_store.delete(document_id=document_id)
            process_success = process_document(filepath, document_id, notebook_id)
            status = "and replaced the existing contents." if process_success else "but semantic indexing failed during update."
            return f"Successfully modified the existing document (ID {document_id}) {status}"
        else:
            new_doc_id = add_document(notebook_id, new_filename, filepath)
            process_success = process_document(filepath, new_doc_id, notebook_id)
            status = "and is ready for use in a new file." if process_success else "but semantic indexing failed."
            return f"Successfully saved the edited document as '{new_filename}' (ID {new_doc_id}) {status}"
            
    except Exception as e:
        return f"Error removing pages: {str(e)}"

