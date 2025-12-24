
// DOM Elements
const chatContainer = document.getElementById('chat-container');
const queryInput = document.getElementById('query-input');
const sendBtn = document.getElementById('send-btn');
const loading = document.getElementById('loading');

const exportBtn = document.getElementById('export-btn-panel');
const ttsBtn = document.getElementById('tts-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');
const settingsBtn = document.getElementById('settings-btn');
const historyModal = document.getElementById('history-modal');
const snippetsModal = document.getElementById('snippets-modal');
const settingsModal = document.getElementById('settings-modal');

const chatSidebar = document.getElementById('chat-sidebar');
const chatHistoryList = document.getElementById('chat-history-list');
const newChatBtn = document.getElementById('new-chat-btn');

// State
let chatHistory = [];
let currentSnippets = [];
let settings = {
    voiceVolume: 100,
    voiceRate: 0.9,
    voicePitch: 1.0,
    theme: 'dark'
};
let ttsActive = false;
let currentUtterance = null;
let currentChatId = null;

// FUNCTION DEFINITIONS
function loadSettings() {
    const stored = localStorage.getItem('docuMindSettings');
    if (stored) {
        settings = { ...settings, ...JSON.parse(stored) };
        applySettings();
    }
}

function saveSettings() {
    localStorage.setItem('docuMindSettings', JSON.stringify(settings));
}

function applySettings() {
    document.getElementById('voice-volume').value = settings.voiceVolume;
    document.getElementById('voice-rate').value = settings.voiceRate;
    document.getElementById('voice-pitch').value = settings.voicePitch;
    document.getElementById('volume-value').textContent = settings.voiceVolume + '%';
    document.getElementById('rate-value').textContent = settings.voiceRate.toFixed(1) + 'x';
    document.getElementById('pitch-value').textContent = settings.voicePitch.toFixed(1) + 'x';

    document.body.className = 'theme-' + settings.theme;
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === settings.theme);
    });
}

function showError(message) {
    showToast(message, 'error');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function addMessage(text, sender, citedFiles = [], confidenceScore = null, sourceSnippets = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = sender === 'user' ? 'You' : 'Assistant';

    const content = document.createElement('div');
    content.className = 'message-content';
    // Use Pre-wrap for raw text for now, we will add marked later
    content.style.whiteSpace = 'pre-wrap';
    content.textContent = text;

    messageDiv.appendChild(label);
    messageDiv.appendChild(content);

    if (sender === 'assistant' && confidenceScore !== null) {
        const confDiv = document.createElement('div');
        confDiv.className = 'confidence-indicator';
        let color = confidenceScore >= 80 ? '#4CAF50' : confidenceScore >= 50 ? '#FFC107' : '#f44336';
        confDiv.innerHTML = `<div class="conf-bar" style="width: ${confidenceScore}%; background: ${color};"></div><span>${confidenceScore}%</span>`;
        content.appendChild(confDiv);
    }

    if (sender === 'assistant' && sourceSnippets && sourceSnippets.length > 0) {
        const btnWrap = document.createElement('div');
        btnWrap.className = 'snippet-actions';
        // Fix spacing between buttons
        btnWrap.style.display = 'flex';
        btnWrap.style.gap = '10px';

        const speakBtn = document.createElement('button');
        speakBtn.className = 'snippet-btn speak-btn';
        speakBtn.textContent = '🔊 Read';
        speakBtn.onclick = () => {
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
                // If we were just reading, we stop.
                // If the user meant "read this instead", they'd click a DIFFERENT button,
                // but simpler logic for now: Click = Toggle Global Speech.
            } else {
                speakText(text);
            }
        };

        const srcBtn = document.createElement('button');
        srcBtn.className = 'snippet-btn';
        srcBtn.textContent = 'View Sources';
        srcBtn.onclick = () => showSourceSnippets(sourceSnippets);

        btnWrap.appendChild(speakBtn);
        btnWrap.appendChild(srcBtn);
        content.appendChild(btnWrap);
    }

    if (citedFiles && citedFiles.length > 0) {
        const citedDiv = document.createElement('div');
        citedDiv.className = 'cited-files';
        const label = document.createElement('div');
        label.className = 'cited-label';
        label.textContent = 'Sources:';
        citedDiv.appendChild(label);
        citedFiles.forEach(filename => {
            const chip = document.createElement('span');
            chip.className = 'file-chip';
            chip.textContent = filename;
            chip.onclick = () => downloadFile(filename);
            citedDiv.appendChild(chip);
        });
        content.appendChild(citedDiv);
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const query = queryInput.value.trim();
    if (!query) return;

    queryInput.value = '';
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();

    addMessage(query, 'user');
    loading.classList.add('active');
    sendBtn.disabled = true;

    // Auto-create chat if none active
    if (!currentChatId) {
        try {
            const res = await fetch('/api/chats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: query.substring(0, 30) })
            });
            const chat = await res.json();
            currentChatId = chat.id;
            loadChatSessions();
        } catch (e) {
            console.error("Session creation error:", e);
        }
    }

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, chat_id: currentChatId })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.answer, 'assistant', data.cited_files, data.confidence_score, data.source_snippets);
            showToast('Response received', 'success');
            // Refresh sessions to update titles if first message
            loadChatSessions();
        } else {
            showError(data.error || 'Error occurred');
        }
    } catch (error) {
        showError('Failed to connect to server');
    } finally {
        loading.classList.remove('active');
        sendBtn.disabled = false;
        queryInput.focus();
    }
}

async function loadChatSessions() {
    if (!chatHistoryList) return;
    try {
        const response = await fetch('/api/chats');
        const chats = await response.json();
        chatHistoryList.innerHTML = '';

        if (chats.length === 0) {
            chatHistoryList.innerHTML = '<div class="loading-history">No history yet</div>';
            return;
        }

        chats.forEach(chat => {
            const item = document.createElement('div');
            item.className = `chat-session-item ${chat.id === currentChatId ? 'active' : ''}`;

            // Title Span
            const titleSpan = document.createElement('span');
            titleSpan.className = 'chat-session-title';
            titleSpan.textContent = chat.title || 'Untitled Chat';
            titleSpan.onclick = () => loadChat(chat.id);

            // Delete Button
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-chat-btn';
            deleteBtn.innerHTML = '🗑️';
            deleteBtn.title = 'Delete Chat';
            deleteBtn.onclick = (e) => {
                e.stopPropagation(); // Prevent opening the chat
                deleteChat(chat.id, chat.title);
            };

            item.appendChild(titleSpan);
            item.appendChild(deleteBtn);
            chatHistoryList.appendChild(item);
        });
    } catch (e) {
        console.error("Load sessions error:", e);
    }
}

// Promise-based Modal Confirmation
function confirmDelete() {
    return new Promise((resolve) => {
        const modal = document.getElementById('delete-confirm-modal');
        const confirmBtn = document.getElementById('confirm-delete-btn');
        const cancelBtn = document.getElementById('cancel-delete-btn');

        modal.style.display = 'block';

        const handleConfirm = () => {
            cleanup();
            resolve(true);
        };

        const handleCancel = () => {
            cleanup();
            resolve(false);
        };

        const cleanup = () => {
            modal.style.display = 'none';
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
        };

        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);

        // Close on outside click
        window.onclick = (event) => {
            if (event.target === modal) {
                handleCancel();
            }
        };
    });
}

async function deleteChat(chatId, title) {
    // Custom Modal Confirmation
    const confirmed = await confirmDelete();
    if (!confirmed) return;

    try {
        const response = await fetch(`/api/chats/${chatId}`, { method: 'DELETE' });
        if (response.ok) {
            showToast('Chat deleted', 'success');

            // If deleted active chat, reset to new chat
            if (currentChatId === chatId) {
                startNewChat();
            } else {
                loadChatSessions(); // Refresh list
            }
        } else {
            showError('Failed to delete chat');
        }
    } catch (e) {
        showError('Error deleting chat');
    }
}

async function loadChat(chatId) {
    if (chatId === currentChatId) return;
    loading.classList.add('active');
    try {
        const response = await fetch(`/api/chats/${chatId}/messages`);
        const messages = await response.json();
        currentChatId = chatId;

        // Clear UI
        document.querySelectorAll('.message').forEach(m => m.remove());
        const welcome = document.querySelector('.welcome-message');
        if (welcome) welcome.remove();

        messages.forEach(m => addMessage(m.text, m.sender, m.cited_files, m.confidence_score, m.source_snippets));
        loadChatSessions(); // Update active highlight
    } catch (e) {
        showError("Failed to load chat");
    } finally {
        loading.classList.remove('active');
    }
}

function startNewChat() {
    currentChatId = null;
    document.querySelectorAll('.message').forEach(m => m.remove());
    if (!document.querySelector('.welcome-message')) {
        chatContainer.innerHTML = `<div class="welcome-message"><h2>Welcome</h2><p>Ask questions about your documents.</p></div>`;
    }
    loadChatSessions();
}

function showSourceSnippets(snippets) {
    const list = document.getElementById('snippets-list');
    list.innerHTML = '';
    snippets.forEach(s => {
        const div = document.createElement('div');
        div.className = 'snippet-card';
        div.innerHTML = `<h4>${s.filename}</h4><p>${s.text}</p>`;
        list.appendChild(div);
    });
    snippetsModal.style.display = 'block';
}

function downloadFile(filename) {
    window.location.href = `/download/${encodeURIComponent(filename)}`;
}

function speakText(text) {
    if (!('speechSynthesis' in window)) return;

    // If speaking the same text or just enabled, this allows restarting or new text
    // But the toggle logic is mainly handled by the button click now.
    // This function just "starts" speech.

    window.speechSynthesis.cancel(); // Stop any current

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = settings.voiceRate || 0.9;
    utterance.volume = (settings.voiceVolume || 100) / 100;
    utterance.pitch = settings.voicePitch || 1.0;

    utterance.onstart = () => { ttsActive = true; };
    utterance.onend = () => { ttsActive = false; };

    window.speechSynthesis.speak(utterance);
}

// Initialization and Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadChatSessions();

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (queryInput) queryInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });



    if (newChatBtn) newChatBtn.addEventListener('click', startNewChat);

    // Clear Chat Button
    if (clearChatBtn) clearChatBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear this chat?')) {
            if (currentChatId) {
                fetch(`/api/chats/${currentChatId}/messages`, { method: 'DELETE' }) // Hypothetical clear endpoint or just new chat
                    .then(() => startNewChat());
            } else {
                startNewChat();
            }
        }
    });

    // TTS Button (Read/Stop)
    if (ttsBtn) ttsBtn.addEventListener('click', () => {
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            ttsActive = false;
            showToast('Stopped reading', 'info');
            return;
        }

        const messages = document.querySelectorAll('.message.assistant .message-content');
        if (messages.length > 0) {
            const lastMsg = messages[messages.length - 1];
            // Extract pure text
            let text = lastMsg.innerText;
            text = text.replace(/🔊 Read\s*View Sources/g, '').replace(/Sources:.*/g, '').trim();
            speakText(text);
        } else {
            showToast('No message to read', 'warning');
        }
    });

    // ... (Export Button Listener remains here) ...


    // Export Button
    if (exportBtn) exportBtn.addEventListener('click', () => {
        const messages = [];
        document.querySelectorAll('.message').forEach(msg => {
            const sender = msg.classList.contains('user') ? 'User' : 'AI';
            // Clean up text content
            let text = msg.querySelector('.message-content').innerText;
            text = text.replace(/🔊 Read\s*View Sources/g, '').replace(/Sources:.*/g, '').trim();
            messages.push(`[${sender}] ${text}`);
        });

        if (messages.length === 0) {
            showToast('Nothing to export', 'warning');
            return;
        }

        const blob = new Blob([messages.join('\n\n')], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('Chat exported', 'success');
    });



    if (settingsBtn) settingsBtn.addEventListener('click', () => {
        settingsModal.style.display = 'block';
    });

    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => btn.closest('.modal').style.display = 'none');
    });

    // Theme selector
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const theme = btn.dataset.theme;
            settings.theme = theme;
            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            applySettings();
        });
    });

    if (document.getElementById('save-settings-btn')) {
        document.getElementById('save-settings-btn').addEventListener('click', () => {
            settings.voiceVolume = parseInt(document.getElementById('voice-volume').value);
            settings.voiceRate = parseFloat(document.getElementById('voice-rate').value);
            settings.voicePitch = parseFloat(document.getElementById('voice-pitch').value);
            saveSettings();
            settingsModal.style.display = 'none';
            showToast('Settings saved', 'success');
        });
    }
});
