import os
import json
import numpy as np
import faiss

STORE_DIR = os.path.join(os.path.dirname(__file__), '..', 'database', 'faiss_db')
os.makedirs(STORE_DIR, exist_ok=True)
INDEX_FILE = os.path.join(STORE_DIR, 'index.faiss')
META_FILE = os.path.join(STORE_DIR, 'metadata.json')

class FaissStore:
    def __init__(self, dim=3072):
        self.dim = dim
        self.index = None
        self.metadata = []
        self.load()

    def load(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(META_FILE, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            self.metadata = []

    def save(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(META_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add(self, embeddings, metadatas, documents, ids):
        if not embeddings: return
        emb_array = np.array(embeddings).astype('float32')
        
        for i, (meta, doc, doc_id) in enumerate(zip(metadatas, documents, ids)):
            self.metadata.append({
                "id": doc_id,
                "notebook_id": str(meta.get("notebook_id")),
                "document_id": str(meta.get("document_id")),
                "text": doc
            })
            
        self.index.add(emb_array)
        self.save()

    def delete(self, notebook_id=None, document_id=None):
        """Marks items as deleted in metadata. Since indices are fixed, we just filter them out during query."""
        changed = False
        for meta in self.metadata:
            if notebook_id and meta.get("notebook_id") == str(notebook_id):
                meta["deleted"] = True
                changed = True
            if document_id and meta.get("document_id") == str(document_id):
                meta["deleted"] = True
                changed = True
        
        if changed:
            self.save()
            print(f"FAISS: Marked items as deleted for nb={notebook_id}, doc={document_id}")

    def query(self, query_embeddings, n_results=5, where=None):
        if self.index.ntotal == 0:
            return {"documents": [[]]}
            
        q_emb = np.array(query_embeddings).astype('float32')
        
        # We need to retrieve more than n_results because we have to filter manually afterwards
        k = min(self.index.ntotal, max(n_results * 20, 100)) 
        distances, indices = self.index.search(q_emb, k)
        
        results = []
        for d, idx in zip(distances[0], indices[0]):
            if idx == -1 or idx >= len(self.metadata): continue
            meta = self.metadata[idx]
            
            # Skip deleted items
            if meta.get("deleted"): continue
            
            # Apply where filter
            match = True
            if where:
                for k_filter, v_filter in where.items():
                    if meta.get(k_filter) != str(v_filter):
                        match = False
                        break
            
            if match:
                results.append(meta["text"])
                if len(results) >= n_results:
                    break
                    
        return {"documents": [results]}

# Singleton instance
vector_store = FaissStore(dim=3072)
