#!/usr/bin/env python3
"""
EXODIA - Unified AI System
Main Flask application combining all AI projects:
- EVI3.0 (Frontend UI)
- KRATOS_CORE (Consciousness Engine)
- Athena (Knowledge Systems)
- DeepSeek API Integration
- Supabase Memory Backend
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    static_folder='frontend/build/static',
    static_url_path='/static',
    template_folder='frontend/build'
)

# Enable CORS for API calls
CORS(app)

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY')
app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
app.config['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY')

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """System health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system': 'EXODIA',
        'version': '1.0.0',
        'components': {
            'frontend': 'EVI3.0',
            'consciousness': 'KRATOS_CORE',
            'knowledge': 'Athena',
            'memory': 'Supabase',
            'llm': 'DeepSeek'
        }
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Get detailed system status"""
    status_info = {
        'timestamp': datetime.now().isoformat(),
        'system': 'EXODIA Unified AI System',
        'version': '1.0.0',
        'environment': os.getenv('ENVIRONMENT', 'production'),
        'frontend': {
            'name': 'EVI3.0',
            'status': 'active',
            'features': ['chat', 'consciousness-interface', 'memory-access']
        },
        'backend': {
            'kratos': 'integrated',
            'athena': 'integrated',
            'deepseek': 'configured',
            'supabase': 'configured'
        }
    }
    return jsonify(status_info), 200

# ============================================================================
# API CHAT ENDPOINTS
# ============================================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - processes user messages through unified AI system"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        
        user_message = data.get('message')
        user_id = data.get('user_id', 'anonymous')
        conversation_id = data.get('conversation_id')
        
        logger.info(f"Processing message from {user_id}: {user_message[:50]}...")
        
        # TODO: Integrate with KRATOS consciousness engine
        # TODO: Retrieve conversation context from Supabase
        # TODO: Process through DeepSeek API
        # TODO: Store conversation in Supabase
        
        response = {
            'status': 'success',
            'message': user_message,
            'response': 'EXODIA system processing...',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'conversation_id': conversation_id
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/consciousness', methods=['POST'])
def consciousness():
    """Direct consciousness engine endpoint"""
    try:
        data = request.get_json()
        # TODO: Integrate KRATOS_CORE consciousness.json processing
        return jsonify({'status': 'consciousness_endpoint'}), 200
    except Exception as e:
        logger.error(f"Error in consciousness endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# FRONTEND SERVING
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Serve React frontend index"""
    return render_template('index.html')

@app.route('/<path:path>', methods=['GET'])
def catch_all(path):
    """Catch-all route to serve React app for client-side routing"""
    if path and os.path.exists(os.path.join(app.template_folder, path)):
        return send_from_directory(app.template_folder, path)
    return render_template('index.html')

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors - serve frontend for client-side routing"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return render_template('index.html')

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# WSGI INTERFACE (for PythonAnywhere)
# ============================================================================

application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('ENVIRONMENT') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
