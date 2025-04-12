# src/web_server.py

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to sys.path to fix imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Import project modules
from src.vector_db import KnowledgeGraphVectorDB
from src.query_processor import QueryProcessor
from src.ollama_interface import OllamaInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder=os.path.join(project_root, 'web', 'static'),
            template_folder=os.path.join(project_root, 'web', 'templates'))

# Initialize global variables
query_processor = None

# Replace before_first_request with a function that initializes components
def initialize_components():
    global query_processor
    
    try:
        logger.info("Initializing application components...")
        vector_db = KnowledgeGraphVectorDB()
        ollama_interface = OllamaInterface(model_name="llama3")
        query_processor = QueryProcessor(vector_db=vector_db, ollama_interface=ollama_interface)
        logger.info("Components initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        print(f"Error: {e}")
        print("Make sure Ollama is installed and running, and the vector database is built.")
        print("To install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("To build the vector database: python src/main.py build")
        return False

# API route for processing queries
@app.route('/api/query', methods=['POST'])
def process_query():
    global query_processor
    
    # Initialize components if not already initialized
    if query_processor is None:
        success = initialize_components()
        if not success:
            return jsonify({'error': 'Failed to initialize components'}), 500
    
    try:
        # Get question from request
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Process query
        logger.info(f"Processing query: {question}")
        result = query_processor.process_query(question)
        
        # Return result
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500

# Serve main page
@app.route('/')
def index():
    return render_template('index.html')

def main(host='0.0.0.0', port=5000, debug=True):
    """Run the web server."""
    print(f"\n{'='*50}")
    print("Knowledge Graph Query System - Web Interface")
    print(f"Running on http://{host}:{port}")
    print("="*50 + "\n")
    
    # Ensure the web directory structure exists
    web_dir = os.path.join(project_root, 'web')
    templates_dir = os.path.join(web_dir, 'templates')
    static_dir = os.path.join(web_dir, 'static')
    css_dir = os.path.join(static_dir, 'css')
    js_dir = os.path.join(static_dir, 'js')
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)
    
    # Initialize components before starting the server
    initialize_components()
    
    # Run the Flask app
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()