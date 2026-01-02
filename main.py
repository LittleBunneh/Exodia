from flask import Flask, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Exodia AI Platform"}), 200

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'False') == 'True'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
