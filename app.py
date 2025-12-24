"""
Universal RAG System - Flask Application
"""

from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import logging
import os

from core import DatabaseManager, LLMService
from core.classifier import DocumentClassifier
from core.chat_manager import ChatManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / os.environ.get('CHROMA_DB_DIR', 'chroma_db_v2')
SORTED_DIR = DATA_DIR / "sorted"

# Initialize services
db_manager = DatabaseManager(DB_DIR)
llm_service = LLMService(model='llama3.2')
classifier = DocumentClassifier()
chat_manager = ChatManager(DATA_DIR)

logger.info(f"✅ Database initialized with {db_manager.get_count()} documents")


@app.route('/')
def index():
    """Render main chat interface"""
    return render_template('index.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test endpoint"""
    return jsonify({'status': 'OK', 'message': 'Server is running'})


# --- Chat History APIs ---
@app.route('/api/chats', methods=['GET'])
def get_chats():
    """Get all chat sessions"""
    return jsonify(chat_manager.get_chats())

@app.route('/api/chats', methods=['POST'])
def create_chat():
    """Create a new chat session"""
    data = request.json or {}
    title = data.get('title', 'New Chat')
    chat = chat_manager.create_chat(title)
    return jsonify(chat)

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat session"""
    chat_manager.delete_chat(chat_id)
    return jsonify({'status': 'success'})

@app.route('/api/chats/<chat_id>/messages', methods=['GET'])
def get_messages(chat_id):
    """Get messages for a specific chat"""
    messages = chat_manager.get_messages(chat_id)
    return jsonify(messages)

@app.route('/api/chats/<chat_id>/title', methods=['PUT'])
def update_title(chat_id):
    """Update chat title"""
    data = request.json
    new_title = data.get('title')
    if new_title:
        chat_manager.update_title(chat_id, new_title)
    return jsonify({'status': 'success'})



@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat queries"""
    try:
        data = request.get_json(silent=True)
        if data and 'message' in data:
            logger.info(f"⚡ RECEIVED REQUEST: {data['message']}")
        
        if not data:
            return jsonify({'error': 'Invalid request'}), 400
        
        query = str(data.get('query', '')).strip()
        chat_id = data.get('chat_id')
        
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        # Increase search window to capture relevant chunks that might have lower vector score
        # Get documents
        # V6: Increase to 25 for Re-ranking (CrossEncoder will filter to Top 5)
        chunks = db_manager.query(query, n_results=25)
        
        if not chunks:
            response = {
                'answer': 'No relevant documents found.',
                'cited_files': [],
                'confidence_score': 0,
                'source_snippets': []
            }
        else:
            answer, cited_files, confidence_score, source_snippets = llm_service.generate_response(query, chunks)
            response = {
                'answer': answer,
                'cited_files': cited_files,
                'confidence_score': confidence_score,
                'source_snippets': source_snippets
            }
            
        # Save to chat history if chat_id provided
        if chat_id:
            messages = chat_manager.get_messages(chat_id)
            messages.append({
                "sender": "user", 
                "text": query, 
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            messages.append({
                "sender": "assistant", 
                "text": response['answer'], 
                "cited_files": response['cited_files'],
                "confidence_score": response['confidence_score'],
                "source_snippets": response['source_snippets'],
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
            chat_manager.save_messages(chat_id, messages)
            
            # Auto-update title if it's the first message and title is currently generic
            if len(messages) <= 2:
                 # Simple heuristic: first few words of query
                 new_title = (query[:30] + '...') if len(query) > 30 else query
                 chat_manager.update_title(chat_id, new_title)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/classify', methods=['POST'])
def classify():
    """Classify given text/filename into Domain/Category with confidence.

    Request JSON:
    - text: Optional string content to classify
    - filename: Optional filename to aid classification

    Returns JSON with: domain, category, file_extension, confidence,
    domain_score, category_score.
    """
    try:
        data = request.get_json(silent=True) or {}
        text = str(data.get('text') or '').strip()
        filename = str(data.get('filename') or '').strip()

        if not text and not filename:
            return jsonify({'error': 'Provide at least text or filename'}), 400

        result = classifier.classify_hierarchical(text or '', filename or '')
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /classify: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    """Download cited file"""
    try:
        # Search for file in sorted directory
        for root, dirs, files in os.walk(SORTED_DIR):
            if filename in files:
                filepath = os.path.join(root, filename)
                return send_file(filepath, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/export-chat', methods=['POST'])
def export_chat():
    """Export chat history as JSON or TXT"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'json')
        chat_history = data.get('chat_history', [])
        
        if format_type == 'json':
            response_data = {
                'export_date': __import__('datetime').datetime.now().isoformat(),
                'total_messages': len(chat_history),
                'chat_history': chat_history
            }
            return jsonify(response_data)
        
        elif format_type == 'txt':
            txt_content = "DocuMind AI - Chat History\n"
            txt_content += f"Exported: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            txt_content += "=" * 60 + "\n\n"
            
            for msg in chat_history:
                txt_content += f"[{msg.get('timestamp', 'N/A')}] {msg.get('sender', 'Unknown')}\n"
                txt_content += f"{msg.get('text', '')}\n"
                if msg.get('confidence_score') is not None:
                    txt_content += f"Confidence: {msg.get('confidence_score', 0)}%\n"
                txt_content += "-" * 60 + "\n\n"
            
            return {'content': txt_content, 'format': 'txt'}
        
        return jsonify({'error': 'Unsupported format'}), 400
        
    except Exception as e:
        logger.error(f"Error exporting chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def status():
    """Get system status"""
    try:
        doc_count = db_manager.get_count()
        
        # Count files in sorted directory
        sorted_files = 0
        categories = []
        for category_dir in SORTED_DIR.iterdir():
            if category_dir.is_dir():
                categories.append(category_dir.name)
                sorted_files += len(list(category_dir.glob('*')))
        
        return jsonify({
            'database_count': doc_count,
            'sorted_files': sorted_files,
            'categories': categories,
            'ollama_available': llm_service.check_availability()
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


def check_ollama():
    """Check if Ollama is available"""
    try:
        ollama.list()
        return True
    except:
        return False


if __name__ == '__main__':
    logger.info("🚀 Starting DocuMind AI...")
    logger.info(f"📁 Database: {DB_DIR}")
    logger.info(f"📚 Documents: {db_manager.get_count()}")
    
    app.run(
        debug=False,  # Disable debug for stability
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )
    # Trigger reload
