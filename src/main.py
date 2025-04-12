# src/main.py

import argparse
from pathlib import Path
import os
import sys
import logging
from vector_db import KnowledgeGraphVectorDB
from query_processor import QueryProcessor
from ollama_interface import OllamaInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_knowledge_graph():
    """Process the knowledge graph."""
    from process_knowledge_graph import main as process_main
    process_main()

def build_vector_db():
    """Build the vector database."""
    from vector_db import main as vector_db_main
    vector_db_main()

def interactive_mode(model_name="llama3", results=3):
    """Start interactive mode."""
    print("\n" + "="*50)
    print("Knowledge Graph Query System - Interactive Mode")
    print(f"Using Ollama with model: {model_name}")
    print("Type 'exit' or 'quit' to exit")
    print("="*50 + "\n")
    
    try:
        # Initialize components
        ollama_interface = OllamaInterface(model_name=model_name)
        vector_db = KnowledgeGraphVectorDB()
        processor = QueryProcessor(vector_db=vector_db, ollama_interface=ollama_interface)
        
        while True:
            # Get user input
            try:
                user_question = input("\nEnter your question: ")
            except EOFError:
                break
            
            # Check for exit command
            if user_question.lower() in ['exit', 'quit', 'q']:
                break
            
            # Skip empty questions
            if not user_question.strip():
                continue
            
            # Process query
            result = processor.process_query(user_question, n_results=results)
            
            # Print answer
            print("\n" + "-"*50)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Answer: {result['answer']}")
            print("-"*50)
    
    except Exception as e:
        logger.error(f"Error in interactive mode: {e}")
        print(f"\nError: {e}")
        print("Make sure Ollama is installed and running.")
        print("To install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("To run Ollama: Just restart your terminal or run 'ollama serve' in a separate terminal")

def main():
    """Main entry point for the application."""
    # Create argument parser
    parser = argparse.ArgumentParser(description='Knowledge Graph Vector Database with Ollama')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Process knowledge graph command
    subparsers.add_parser('process', help='Process the knowledge graph')
    
    # Build vector database command
    subparsers.add_parser('build', help='Build the vector database')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive mode')
    interactive_parser.add_argument('--results', type=int, default=3, help='Number of results to return')
    interactive_parser.add_argument('--model', default='llama3', help='Ollama model name to use')
    
    # Run all command
    subparsers.add_parser('all', help='Run process, build, and start interactive mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run command
    if args.command == 'process':
        process_knowledge_graph()
    elif args.command == 'build':
        build_vector_db()
    elif args.command == 'interactive':
        interactive_mode(model_name=args.model, results=args.results)
    elif args.command == 'all':
        print("=== Processing Knowledge Graph ===")
        process_knowledge_graph()
        print("\n=== Building Vector Database ===")
        build_vector_db()
        print("\n=== Starting Interactive Mode ===")
        interactive_mode()
    else:
        # Default to interactive mode if no command specified
        interactive_mode()

if __name__ == "__main__":
    main()