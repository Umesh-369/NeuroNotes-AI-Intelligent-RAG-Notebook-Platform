import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from database.models import (
    init_db, create_user, get_user_by_email, create_notebook,
    get_user_notebooks, delete_notebook, add_document,
    get_notebook_documents, save_insight, get_notebook_insights, delete_insight,
    get_document_by_id, delete_document
)
from rag.document_processor import process_document
from rag.chatbot import query_rag
from rag.faiss_store import vector_store
from rag.agent import agent_app
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super_secret_dev_key")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure database is initialized
init_db()

# ---- Authentication Routes ----

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    data = request.get_json(silent=True) if request.is_json else request.form
    email = data.get('email')
    password = data.get('password')
    
    user = get_user_by_email(email)
    if user and user['password'] == password:
        session['user_id'] = user['id']
        session['email'] = user['email']
        # Return JSON if it was an AJAX request, else redirect
        if request.is_json:
            return jsonify({"success": True, "message": "Logged in successfully"})
        return redirect(url_for('dashboard'))
    
    if request.is_json:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    return render_template('login.html', error="Invalid email or password")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
        
    data = request.get_json(silent=True) if request.is_json else request.form
    email = data.get('email')
    password = data.get('password')
    
    if create_user(email, password):
        if request.is_json:
            return jsonify({"success": True, "message": "User created. Please log in."})
        return redirect(url_for('login'))
    
    if request.is_json:
        return jsonify({"success": False, "message": "Email already exists"}), 400
    return render_template('signup.html', error="Email already exists")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---- Dashboard & Notebooks ----

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', email=session.get('email'))

@app.route('/notebooks', methods=['GET'])
def list_notebooks():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    notebooks = get_user_notebooks(session['user_id'])
    return jsonify({"notebooks": notebooks})

@app.route('/create_notebook', methods=['POST'])
def create_new_notebook():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    title = data.get('title')
    desc = data.get('description', '')
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    notebook_id = create_notebook(session['user_id'], title, desc)
    return jsonify({"success": True, "notebook_id": notebook_id, "title": title})

@app.route('/delete_notebook/<int:notebook_id>', methods=['DELETE'])
def del_notebook(notebook_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    # 1. Clean up FAISS
    vector_store.delete(notebook_id=notebook_id)
    
    # 2. Clean up Files
    docs = get_notebook_documents(notebook_id)
    for doc in docs:
        if os.path.exists(doc['filepath']):
            try:
                os.remove(doc['filepath'])
            except:
                pass
                
    # 3. Clean up DB
    delete_notebook(notebook_id, session['user_id'])
    return jsonify({"success": True})

# ---- Document Routes ----

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if 'file' not in request.files or 'notebook_id' not in request.form:
        return jsonify({"error": "File and notebook_id are required"}), 400
        
    file = request.files['file']
    notebook_id = request.form['notebook_id']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Save to DB
    doc_id = add_document(notebook_id, filename, filepath)
    
    # Process for RAG
    success = process_document(filepath, doc_id, notebook_id)
    if success:
        return jsonify({"success": True, "message": "File uploaded and processed", "doc_id": doc_id})
    else:
        return jsonify({"success": False, "error": "File uploaded but extraction/embedding failed"}), 500

@app.route('/documents/<int:notebook_id>', methods=['GET'])
def list_documents(notebook_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    docs = get_notebook_documents(notebook_id)
    return jsonify({"documents": docs})

@app.route('/delete_document/<int:doc_id>', methods=['DELETE'])
def del_document(doc_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    doc = get_document_by_id(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
        
    # 1. Clean up FAISS
    vector_store.delete(document_id=doc_id)
    
    # 2. Clean up File
    if os.path.exists(doc['filepath']):
        try:
            os.remove(doc['filepath'])
        except:
            pass
            
    # 3. Clean up DB
    delete_document(doc_id)
    return jsonify({"success": True})

@app.route('/download/<int:doc_id>', methods=['GET'])
def download_document(doc_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    doc = get_document_by_id(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
        
    if not os.path.exists(doc['filepath']):
        return jsonify({"error": "File not found on disk"}), 404
        
    return send_file(doc['filepath'], as_attachment=True, download_name=doc['filename'])

@app.route('/rag-query', methods=['POST'])
def rag_query():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    query = data.get('query')
    notebook_id = data.get('notebook_id')
    document_id = data.get('document_id', None)
    
    if not query or not notebook_id:
        return jsonify({"error": "Missing query or notebook_id"}), 400
        
    response = query_rag(query, notebook_id, document_id)
    return jsonify(response)

@app.route('/agent-query', methods=['POST'])
def agent_query():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    query = data.get('query')
    notebook_id = data.get('notebook_id')
    
    if not query or not notebook_id:
        return jsonify({"error": "Missing query or notebook_id"}), 400
        
    try:
        from langchain_core.messages import HumanMessage
        
        # Unique thread ID for chat memory within this specific notebook for this user
        thread_id = f"user_{session['user_id']}_notebook_{notebook_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "notebook_id": notebook_id
        }
        
        # Invoke LangGraph agent
        final_state = agent_app.invoke(initial_state, config=config)
        
        final_message = final_state["messages"][-1].content
        
        # Gemini often returns content as a list of dicts. We must extract the strings.
        if isinstance(final_message, list):
            text_parts = []
            for item in final_message:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
            final_message = "\n".join(text_parts)
        elif not isinstance(final_message, str):
            final_message = str(final_message)
            
        import re
        final_message = re.sub(r'[*_#]+', '', final_message)
        final_message = final_message.replace('`', '')
        
        return jsonify({"answer": final_message, "sources": []})
        
    except Exception as e:
        print(f"Agent Error: {str(e)}")
        return jsonify({"answer": f"Sorry, the agent encountered an internal error: {str(e)}", "sources": []})

# ---- Insights API ----

@app.route('/save_insight', methods=['POST'])
def save_new_insight():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    notebook_id = data.get('notebook_id')
    content = data.get('content')
    
    if not notebook_id or not content:
        return jsonify({"error": "Missing notebook_id or content"}), 400
        
    insight_id = save_insight(notebook_id, content)
    return jsonify({"success": True, "insight_id": insight_id})

@app.route('/insights', methods=['GET'])
def list_insights():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    notebook_id = request.args.get('notebook_id')
    if not notebook_id:
        return jsonify({"error": "Missing notebook_id parameter"}), 400
        
    insights = get_notebook_insights(notebook_id)
    return jsonify({"insights": insights})

@app.route('/delete_insight/<int:insight_id>', methods=['DELETE'])
def del_insight(insight_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    delete_insight(insight_id)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
