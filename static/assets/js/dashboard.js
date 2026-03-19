/**
 * dashboard.js
 * Handles all frontend interactions for NeuroNotes Dashboard
 */

document.addEventListener('DOMContentLoaded', () => {
    let activeNotebookId = null;
    let activeDocumentId = null;

    // DOM Elements
    const notebookListEl = document.getElementById('notebook-list');
    const documentListEl = document.getElementById('document-list');
    const insightsListEl = document.getElementById('insights-list');
    const chatHistoryEl = document.getElementById('chat-history');

    const activeNbTitleEl = document.getElementById('active-notebook-title');
    const activeNbMetaEl = document.getElementById('active-notebook-meta');

    const chatInput = document.getElementById('chat-input');
    const btnSendChat = document.getElementById('btn-send-chat');

    const btnUploadTrigger = document.getElementById('btn-upload-trigger');
    const fileUpload = document.getElementById('file-upload');
    const btnNewNotebook = document.getElementById('btn-new-notebook');

    const btnSummarize = document.getElementById('btn-summarize');
    const btnExtractInsights = document.getElementById('btn-extract-insights');
    const searchInsightsInput = document.getElementById('search-insights-input');

    // Modal Elements
    const confirmModal = document.getElementById('confirm-modal');
    const modalTitleEl = document.getElementById('modal-title');
    const modalBodyEl = document.getElementById('modal-body');
    const btnModalCancel = document.getElementById('btn-modal-cancel');
    const btnModalConfirm = document.getElementById('btn-modal-confirm');

    let modalResolve = null;

    // ==========================================
    // INITIALIZATION & NOTEBOOKS
    // ==========================================
    async function initDashboard() {
        await loadNotebooks();
    }

    async function loadNotebooks() {
        try {
            const res = await fetch('/notebooks');
            if (res.status === 401) {
                window.location.href = '/login';
                return;
            }
            const data = await res.json();

            notebookListEl.innerHTML = '';

            if (data.notebooks && data.notebooks.length > 0) {
                data.notebooks.forEach(nb => {
                    const li = document.createElement('li');
                    li.className = activeNotebookId === nb.id ? 'active' : '';
                    li.innerHTML = `
                        <div class="flex items-center flex-1" onclick="selectNotebookById(${nb.id})">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none" class="mr-2">
                                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                            </svg>
                            ${nb.title}
                        </div>
                        <button class="delete-icon" onclick="handleDeleteNotebook(event, ${nb.id}, '${nb.title.replace(/'/g, "\\'")}')" title="Delete Notebook">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                        </button>
                    `;
                    notebookListEl.appendChild(li);
                });

                // Auto-select first notebook if none selected
                if (!activeNotebookId || !data.notebooks.find(n => n.id === activeNotebookId)) {
                    selectNotebook(data.notebooks[0]);
                }
            } else {
                notebookListEl.innerHTML = '<li class="text-muted" style="font-size: 0.8em; padding-left: 10px;">No notebooks yet. Create one!</li>';
                activeNbTitleEl.textContent = 'Welcome to NeuroNotes';
                activeNbMetaEl.textContent = 'Create a notebook to get started';
            }
        } catch (e) {
            console.error("Failed to load notebooks", e);
        }
    }

    // Helper to select notebook by ID (used in template literal)
    window.selectNotebookById = async function (id) {
        const res = await fetch('/notebooks');
        const data = await res.json();
        const nb = data.notebooks.find(n => n.id === id);
        if (nb) selectNotebook(nb);
    }

    async function selectNotebook(nb) {
        activeNotebookId = nb.id;
        activeDocumentId = null; // reset active document when changing notebooks
        activeNbTitleEl.innerHTML = `${nb.title}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="ml-2 cursor-pointer" onclick="deleteActiveNotebook()" title="Delete Notebook">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
        `;

        // Re-render list to show active state
        Array.from(notebookListEl.children).forEach(child => {
            if (child.textContent.includes(nb.title)) {
                child.classList.add('active');
            } else {
                child.classList.remove('active');
            }
        });

        // Load content for this notebook
        loadDocuments(nb.id);
        loadInsights(nb.id);

        // Reset chat
        chatHistoryEl.innerHTML = `
            <div class="chat-greeting text-center" style="padding-top: 40px; margin-bottom: 2rem;">
                <div class="ai-sparkles" style="margin: 0 auto; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: rgba(var(--primary-rgb), 0.1); border-radius: 50%; color: var(--primary-color);">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
                    </svg>
                </div>
                <h2 style="margin-top: 1rem;">Research Assistant</h2>
                <p class="text-muted">Ask me anything about your documents in this notebook.</p>
            </div>
        `;
    }

    window.deleteActiveNotebook = async function () {
        if (!activeNotebookId) return;
        const confirmed = await showConfirmModal("Delete Notebook?", "Are you sure you want to delete this notebook and all its documents?");
        if (!confirmed) return;

        try {
            await fetch(`/delete_notebook/${activeNotebookId}`, { method: 'DELETE' });
            activeNotebookId = null;
            loadNotebooks();
        } catch (e) {
            showToast("Unable to delete. Please try again.");
            console.error(e);
        }
    }

    window.handleDeleteNotebook = async function (e, id, title) {
        e.stopPropagation();
        const li = e.target.closest('li');
        
        const confirmed = await showConfirmModal("Delete Notebook?", `Are you sure you want to delete "${title}" and all its contents?`);
        if (!confirmed) return;

        if (li) li.classList.add('fadeOut');

        try {
            const res = await fetch(`/delete_notebook/${id}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) {
                setTimeout(() => {
                    if (activeNotebookId === id) {
                        activeNotebookId = null;
                    }
                    loadNotebooks();
                }, 400);
            } else {
                li.classList.remove('fadeOut');
                showToast("Unable to delete. Please try again.");
            }
        } catch (err) {
            li.classList.remove('fadeOut');
            showToast("Unable to delete. Please try again.");
        }
    }

    window.handleDownloadDocument = function (e, id) {
        e.stopPropagation();
        window.location.href = `/download/${id}`;
    }

    window.handleDeleteDocument = async function (e, id, filename) {
        e.stopPropagation();
        const docEl = e.target.closest('.doc-item');
        
        const confirmed = await showConfirmModal("Delete Document?", `Are you sure you want to delete "${filename}"?`);
        if (!confirmed) return;

        if (docEl) docEl.classList.add('fadeOut');

        try {
            const res = await fetch(`/delete_document/${id}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) {
                setTimeout(() => {
                    if (activeDocumentId === id) {
                        activeDocumentId = null;
                    }
                    loadDocuments(activeNotebookId);
                }, 400);
            } else {
                docEl.classList.remove('fadeOut');
                showToast("Unable to delete. Please try again.");
            }
        } catch (err) {
            docEl.classList.remove('fadeOut');
            showToast("Unable to delete. Please try again.");
        }
    }

    // Modal Helpers
    function showConfirmModal(title, body) {
        modalTitleEl.textContent = title;
        modalBodyEl.textContent = body;
        confirmModal.classList.add('show');
        return new Promise((resolve) => {
            modalResolve = resolve;
        });
    }

    btnModalCancel.onclick = () => {
        confirmModal.classList.remove('show');
        if (modalResolve) modalResolve(false);
    };

    btnModalConfirm.onclick = () => {
        confirmModal.classList.remove('show');
        if (modalResolve) modalResolve(true);
    };

    function showToast(msg) {
        // Simple alert for now, can be improved to a nice toast later
        alert(msg);
    }

    btnNewNotebook.addEventListener('click', () => {
        // Check if there's already an active creation
        if (document.querySelector('.inline-notebook-item')) return;

        const li = document.createElement('li');
        li.className = 'inline-notebook-item';
        li.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="var(--primary-color)" stroke="none">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
            <input type="text" class="inline-notebook-input" value="Untitled Notebook" spellcheck="false">
        `;

        // Add to the bottom of the list
        notebookListEl.appendChild(li);

        const input = li.querySelector('input');
        input.focus();
        input.select();

        let isSaving = false;

        const handleSave = async () => {
            if (isSaving) return;
            const title = input.value.trim();
            if (!title) {
                li.remove();
                return;
            }

            isSaving = true;
            input.disabled = true;
            li.style.opacity = '0.7';

            try {
                const res = await fetch('/create_notebook', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: title })
                });
                const data = await res.json();
                if (data.success) {
                    activeNotebookId = data.notebook_id;
                    await loadNotebooks();
                } else {
                    alert("Failed to create notebook: " + (data.error || "Unknown error"));
                    li.remove();
                }
            } catch (e) {
                console.error(e);
                li.remove();
            }
        };

        const handleCancel = () => {
            if (!isSaving) {
                li.remove();
            }
        };

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                handleSave();
            } else if (e.key === 'Escape') {
                handleCancel();
            }
        });

        input.addEventListener('blur', () => {
            // Short delay to allow click events on the same element if needed, 
            // but requirement says cancel on click outside/blur.
            setTimeout(() => {
                handleCancel();
            }, 100);
        });
    });

    // ==========================================
    // DOCUMENTS & UPLOADS
    // ==========================================
    async function loadDocuments(nbId) {
        documentListEl.innerHTML = '<div style="font-size: 0.8em; color: var(--text-muted); padding: 10px;">Loading...</div>';
        try {
            const res = await fetch(`/documents/${nbId}`);
            const data = await res.json();

            documentListEl.innerHTML = '';

            if (data.documents && data.documents.length > 0) {
                activeNbMetaEl.textContent = `${data.documents.length} Documents • Active Notebook Workspace`;

                data.documents.forEach(doc => {
                    const docEl = document.createElement('div');
                    docEl.className = `doc-item ${activeDocumentId === doc.id ? 'active' : ''}`;
                    docEl.style.cursor = 'pointer';
                    // We can add an active class highlighting later if needed
                    if (activeDocumentId === doc.id) {
                        docEl.style.backgroundColor = 'rgba(var(--primary-rgb), 0.05)';
                        docEl.style.borderLeft = '3px solid var(--primary-color)';
                    }

                    const isPdf = doc.filename.toLowerCase().endsWith('.pdf');
                    docEl.innerHTML = `
                        <div class="flex items-center flex-1">
                            <div class="doc-icon ${isPdf ? 'pdf-icon' : 'md-icon'}">${isPdf ? 'PDF' : 'DOC'}</div>
                            <div class="doc-info">
                                <div class="doc-title">${doc.filename}</div>
                                <div class="doc-meta">Processed • Ready</div>
                            </div>
                        </div>
                        <div class="doc-actions flex items-center">
                            <button class="download-icon mr-2" onclick="handleDownloadDocument(event, ${doc.id})" title="Download Document" style="background: none; border: none; cursor: pointer; color: var(--text-muted);">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                    <polyline points="7 10 12 15 17 10"></polyline>
                                    <line x1="12" y1="15" x2="12" y2="3"></line>
                                </svg>
                            </button>
                            <button class="delete-icon" onclick="handleDeleteDocument(event, ${doc.id}, '${doc.filename.replace(/'/g, "\\'")}')" title="Delete Document">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                            </button>
                        </div>
                    `;

                    docEl.onclick = () => {
                        activeDocumentId = activeDocumentId === doc.id ? null : doc.id; // Toggle active
                        loadDocuments(nbId); // Re-render to show selection
                    };

                    documentListEl.appendChild(docEl);
                });
            } else {
                activeNbMetaEl.textContent = `0 Documents • Empty Workspace`;
                documentListEl.innerHTML = '<div style="font-size: 0.8em; color: var(--text-muted); padding: 10px; text-align: center;">No documents yet.<br>Upload one to get started.</div>';
            }
        } catch (e) {
            console.error(e);
        }
    }

    btnUploadTrigger.addEventListener('click', () => {
        if (!activeNotebookId) {
            alert("Please create or select a notebook first.");
            return;
        }
        fileUpload.click();
    });

    fileUpload.addEventListener('change', async (e) => {
        if (!e.target.files || e.target.files.length === 0) return;
        const file = e.target.files[0];
        if (!activeNotebookId) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('notebook_id', activeNotebookId);

        // UI Loading state
        const originalText = btnUploadTrigger.innerHTML;
        btnUploadTrigger.innerHTML = 'Uploading & Analyzing...';
        btnUploadTrigger.disabled = true;

        try {
            const res = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.success) {
                // Refresh docs
                fileUpload.value = ''; // reset
                loadDocuments(activeNotebookId);
            } else {
                alert("Upload failed: " + (data.error || "Unknown error"));
            }
        } catch (err) {
            alert("An error occurred during upload.");
            console.error(err);
        } finally {
            btnUploadTrigger.innerHTML = originalText;
            btnUploadTrigger.disabled = false;
        }
    });

    // ==========================================
    // CHAT SYSTEM
    // ==========================================
    async function submitChat(forcedQuery = null) {
        if (!activeNotebookId) return;
        const query = forcedQuery || chatInput.value.trim();
        if (!query) return;

        // Clear input early
        if (!forcedQuery) chatInput.value = '';

        // Determine badge text
        const scopeBadge = activeDocumentId ? "Doc Filtered" : "Notebook Search";

        // Append User Message
        const userRow = document.createElement('div');
        userRow.className = 'chat-row user-row';
        userRow.innerHTML = `
            <div class="avatar-container">
                <img src="https://ui-avatars.com/api/?name=User&background=f3f4f6&color=9ca3af" alt="User" class="avatar">
            </div>
            <div class="message-content">
                <div class="message-sender">You</div>
                <div class="message-text">${query}</div>
            </div>
        `;
        chatHistoryEl.appendChild(userRow);

        // Loading AI Row
        const aiRow = document.createElement('div');
        aiRow.className = 'chat-row ai-row';
        aiRow.innerHTML = `
            <div class="avatar-container">
                <div class="ai-avatar pulseGlowSoft">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4 4h16v16H4V4z" />
                    </svg>
                </div>
            </div>
            <div class="message-content">
                <div class="message-sender flex items-center">
                    Research Assistant
                    <span class="rag-badge ml-2">${scopeBadge}</span>
                </div>
                <div class="message-text">
                    <p class="text-muted">Thinking...</p>
                </div>
            </div>
        `;
        chatHistoryEl.appendChild(aiRow);

        // Scroll to bottom
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;

        try {
            const fetchPayload = {
                query: query,
                notebook_id: activeNotebookId
            };
            // Only send document_id if one is explicitly selected
            if (activeDocumentId) {
                fetchPayload.document_id = activeDocumentId;
            }

            const res = await fetch('/rag-query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fetchPayload)
            });
            const data = await res.json();

            // Render actual response
            const msgContent = aiRow.querySelector('.message-content');

            // Markdown formatting (Very basic, safely replacing \n with <br> and stripping other markdown for 'normal text')
            const answerHTML = data.answer
                .replace(/\*\*/g, '') // Strip bold
                .replace(/\*/g, '')  // Strip italic
                .replace(/###/g, '') // Strip headers
                .replace(/##/g, '')
                .replace(/#/g, '')
                .replace(/\n/g, '<br>');

            let sourcesHTML = '';
            if (data.sources && data.sources.length > 0) {
                sourcesHTML = `
                    <div class="sources-block mt-4">
                        <div class="sources-title">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-2">
                                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                            </svg>
                            CONTEXT USED
                        </div>
                        <div class="source-item" style="font-size: 0.8em; line-height: 1.4; max-height: 100px; overflow-y: auto; color: var(--text-muted);">
                            ${data.sources[0].substring(0, 300)}...
                        </div>
                    </div>
                `;
            }

            msgContent.innerHTML = `
                <div class="message-sender flex items-center">
                    Research Assistant
                    <span class="rag-badge ml-2">${scopeBadge}</span>
                </div>
                <div class="message-text">${answerHTML}</div>
                ${sourcesHTML}
            `;

            // Remove pulse
            aiRow.querySelector('.ai-avatar').classList.remove('pulseGlowSoft');

            chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;

            // If this was an automated extract insights, save it!
            if (forcedQuery && forcedQuery.includes('key insights')) {
                await saveInsight(data.answer.substring(0, 50) + '...', data.answer);
            }

        } catch (e) {
            console.error(e);
            aiRow.querySelector('.message-text').innerHTML = '<p class="text-error">An error occurred trying to connect to the AI.</p>';
        }
    }

    btnSendChat.addEventListener('click', () => submitChat());
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitChat();
    });

    // ==========================================
    // INSIGHTS & ACTIONS
    // ==========================================
    btnSummarize.addEventListener('click', () => {
        submitChat("Please provide a comprehensive summary of the current context.");
    });

    btnExtractInsights.addEventListener('click', () => {
        // We do a chat query, and intercept inside submitChat to auto-save it
        submitChat("Please extract 3 key insights from the context into clear bullet points.");
    });

    async function loadInsights(nbId) {
        try {
            const res = await fetch(`/insights?notebook_id=${nbId}`);
            const data = await res.json();

            insightsListEl.innerHTML = '';

            if (data.insights && data.insights.length > 0) {
                data.insights.forEach(ins => {
                    const el = document.createElement('div');
                    el.className = 'insight-card slideInRightFade';

                    // Attempt to parse out a title vs body from markdown
                    let title = "Insight Note";
                    let body = ins.content;
                    if (body.includes('\n')) {
                        const parts = body.split('\n');
                        title = parts[0].replace(/\*|#/g, '').substring(0, 40);
                        body = parts.slice(1).join('<br>').replace(/\*|#/g, '');
                    } else {
                        title = body.replace(/\*|#/g, '').substring(0, 30) + '...';
                        body = body.replace(/\*|#/g, '');
                    }

                    el.innerHTML = `
                        <div class="card-title flex justify-between items-center">
                            ${title}
                            <button class="icon-btn text-muted" onclick="deleteInsight(${ins.id})" style="padding:0">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                            </button>
                        </div>
                        <div class="card-body" style="max-height: 100px; overflow-y: auto;">
                            ${body}
                        </div>
                        <div class="card-footer flex justify-between items-center mt-4">
                            <span class="added-time">Just now</span>
                            <div class="source-badge">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1">
                                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                                </svg>
                                AI Extracted
                            </div>
                        </div>
                    `;
                    insightsListEl.appendChild(el);
                });
            } else {
                insightsListEl.innerHTML = '<div style="font-size: 0.8em; color: var(--text-muted); padding: 10px; text-align: center;">No insights saved yet.<br>Use the Extract button or create one manually!</div>';
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function saveInsight(title, content) {
        if (!activeNotebookId) return;
        try {
            await fetch('/save_insight', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notebook_id: activeNotebookId, content: content })
            });
            loadInsights(activeNotebookId);
        } catch (e) {
            console.error("Failed to save insight", e);
        }
    }



    window.deleteInsight = async function (id) {
        try {
            await fetch(`/delete_insight/${id}`, { method: 'DELETE' });
            loadInsights(activeNotebookId);
        } catch (e) {
            console.error(e);
        }
    }

    // Basic Search Filter for Insights
    searchInsightsInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        Array.from(insightsListEl.children).forEach(card => {
            if (card.textContent.toLowerCase().includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });

    // Profile Dropdown
    const profileBtn = document.getElementById('profile-btn');
    const profileDropdown = document.getElementById('profile-dropdown');

    if (profileBtn && profileDropdown) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            profileDropdown.classList.toggle('show');
            profileDropdown.classList.toggle('hidden');
        });

        document.addEventListener('click', (e) => {
            if (!profileDropdown.contains(e.target) && !profileBtn.contains(e.target)) {
                profileDropdown.classList.remove('show');
                profileDropdown.classList.add('hidden');
            }
        });
    }

    // ==========================================
    // FLOATING AGENT CHAT
    // ==========================================
    const agentChatToggle = document.getElementById('agent-chat-toggle');
    const agentChatPanel = document.getElementById('agent-chat-panel');
    const btnCloseAgent = document.getElementById('btn-close-agent');
    const agentChatHistory = document.getElementById('agent-chat-history');
    const agentChatInput = document.getElementById('agent-chat-input');
    const btnAgentSend = document.getElementById('btn-agent-send');

    if (agentChatToggle && agentChatPanel) {
        agentChatToggle.addEventListener('click', () => {
            agentChatPanel.classList.toggle('hidden');
            if (!agentChatPanel.classList.contains('hidden')) {
                agentChatInput.focus();
            }
        });

        btnCloseAgent.addEventListener('click', () => {
            agentChatPanel.classList.add('hidden');
        });

        async function submitAgentChat() {
            const query = agentChatInput.value.trim();
            if (!query) return;

            agentChatInput.value = '';

            // User Row
            const userRow = document.createElement('div');
            userRow.className = 'chat-row user-row';
            userRow.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${query}</div>
                </div>
            `;
            agentChatHistory.appendChild(userRow);

            // Thinking Row
            const aiRow = document.createElement('div');
            aiRow.className = 'chat-row ai-row';
            aiRow.innerHTML = `
                <div class="message-content" style="display: flex; gap: 0.5rem; justify-content: flex-start; align-items: center;">
                    <div class="thinking-text">Thinking...</div>
                </div>
            `;
            agentChatHistory.appendChild(aiRow);
            agentChatHistory.scrollTop = agentChatHistory.scrollHeight;

            try {
                // Determine if we have a notebook selected
                const payload = { query: query };
                if (activeNotebookId) {
                    payload.notebook_id = activeNotebookId;
                }

                // For this widget, we'll continue using the /chat endpoint but we do not strictly enforce notebook_id 
                // However, our backend /chat explicitly requires notebook_id right now. 
                // We'll pass activeNotebookId if available, otherwise it might fail gracefully.
                if (!activeNotebookId) {
                    aiRow.querySelector('.message-content').innerHTML = `
                        <div class="message-text">Please select a notebook workspace first so I can assist you with your context.</div>
                    `;
                    return;
                }

                const res = await fetch('/agent-query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                if (res.status === 401) {
                    window.location.href = '/login';
                    return;
                }

                if (data.error) {
                    aiRow.querySelector('.message-content').innerHTML = `<div class="message-text text-error">${data.error}</div>`;
                    return;
                }

                const answerHTML = data.answer.replace(/\n/g, '<br>');
                aiRow.querySelector('.message-content').innerHTML = `
                    <div class="message-text">${answerHTML}</div>
                `;
                agentChatHistory.scrollTop = agentChatHistory.scrollHeight;

            } catch (err) {
                console.error(err);
                aiRow.querySelector('.message-content').innerHTML = `
                    <div class="message-text text-error">Could not reach the agent backend. Please try again.</div>
                `;
            }
        }

        btnAgentSend.addEventListener('click', submitAgentChat);
        agentChatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') submitAgentChat();
        });
    }

    // Start App
    initDashboard();
});
