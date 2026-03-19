import os
import google.generativeai as genai
from rag.document_processor import configure_gemini
from rag.faiss_store import vector_store

def query_rag(query, notebook_id, document_id=None):
    configure_gemini()
    try:
        if not os.environ.get("GOOGLE_API_KEY"):
            return {"answer": "GOOGLE_API_KEY is not set. Please set it to use the AI features.", "sources": []}
            
        # Embed the query
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = response['embedding']
        
        where_filter = {"notebook_id": str(notebook_id)}
        if document_id:
            where_filter["document_id"] = str(document_id)
        
        # Query FAISS
        results = vector_store.query(
            query_embeddings=[query_embedding],
            n_results=5,
            where=where_filter
        )
        
        # Construct Context
        context_chunks = results['documents'][0] if (results and 'documents' in results and results['documents']) else []
        context = "\n".join(context_chunks)
        
        if not context.strip():
            context = "No relevant context found in this notebook's documents. Answer from general knowledge if appropriate, but specify that the info is not from the documents."
            
        # Call Gemini Chat
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an AI research assistant. Use the following context retrieved from the user's documents to answer the question.
        
        Context:
        {context}
        
        Question:
        {query}
        
        Answer professionally and cite information from the context where appropriate.
        IMPORTANT: Provide your answer in plain text ONLY. Do NOT use markdown symbols like **bold**, # headers, or - bullet points. Use clear paragraphs.
        """
        
        chat_response = model.generate_content(prompt)
        return {"answer": chat_response.text, "sources": context_chunks}
    except Exception as e:
        print(f"RAG Error: {e}")
        return {"answer": f"Sorry, an error occurred while processing your request: {e}", "sources": []}
