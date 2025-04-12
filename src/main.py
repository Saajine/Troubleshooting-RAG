# src/main.py

import argparse
from pathlib import Path
import os
import sys
import unittest
import logging

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

def query_vector_db(query_text, results=3):
    """Query the vector database."""
    from vector_db import KnowledgeGraphVectorDB
    
    # Initialize vector database
    vector_db = KnowledgeGraphVectorDB()
    
    # Query database
    results = vector_db.query(query_text, n_results=results)
    
    # Display results
    print(f"\nQuery: '{query_text}'")
    print(f"Found {len(results['documents'][0])} relevant results:\n")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        relevance = 1 - distance
        print(f"=== Result {i+1} (Relevance: {relevance:.2f}) ===")
        print(f"Title: {metadata['title']}")
        print(f"Severity: {metadata['severity']}")
        print("\nContent Preview:")
        preview = doc.split('\n')[0:5]
        print('\n'.join(preview))
        print("\n" + "="*50 + "\n")

def query_knowledge_graph(args):
    """Query the knowledge graph with LLM."""
    from cli import process_single_query
    process_single_query(args)

def interactive_mode(args):
    """Start interactive mode."""
    from cli import interactive_mode
    interactive_mode(args)

def run_tests():
    """Run unit tests."""
    # Discover and run tests
    test_loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')
    test_suite = test_loader.discover(start_dir, pattern='test_*.py')
    test_result = unittest.TextTestRunner().run(test_suite)
    return test_result.wasSuccessful()

def main():
    """Main entry point for the application."""
    # Create argument parser
    parser = argparse.ArgumentParser(description='Knowledge Graph Vector Database with LLM')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Process knowledge graph command
    subparsers.add_parser('process', help='Process the knowledge graph')
    
    # Build vector database command
    subparsers.add_parser('build', help='Build the vector database')
    
    # Vector DB Query command (simple)
    vector_query_parser = subparsers.add_parser('vector-query', help='Simple vector database query')
    vector_query_parser.add_argument('query_text', help='The query text')
    vector_query_parser.add_argument('--results', type=int, default=3, help='Number of results to return')
    
    # LLM Query command
    llm_query_parser = subparsers.add_parser('query', help='Query with LLM support')
    llm_query_parser.add_argument('question', help='User question')
    llm_query_parser.add_argument('--results', type=int, default=3, help='Number of results to return')
    llm_query_parser.add_argument('--model', choices=['huggingface', 'llama.cpp'], default='huggingface', 
                                  help='LLM model type')
    llm_query_parser.add_argument('--model-path', default='meta-llama/Llama-3-8B-Instruct', 
                                  help='Path to the model')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive mode')
    interactive_parser.add_argument('--results', type=int, default=3, help='Number of results to return')
    interactive_parser.add_argument('--model', choices=['huggingface', 'llama.cpp'], default='huggingface', 
                                   help='LLM model type')
    interactive_parser.add_argument('--model-path', default='meta-llama/Llama-3-8B-Instruct', 
                                   help='Path to the model')
    
    # Run tests command
    subparsers.add_parser('test', help='Run unit tests')
    
    # Run all command
    subparsers.add_parser('all', help='Run process, build, and test')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run command
    if args.command == 'process':
        process_knowledge_graph()
    elif args.command == 'build':
        build_vector_db()
    elif args.command == 'vector-query':
        query_vector_db(args.query_text, args.results)
    elif args.command == 'query':
        query_knowledge_graph(args)
    elif args.command == 'interactive':
        interactive_mode(args)
    elif args.command == 'test':
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.command == 'all':
        print("=== Processing Knowledge Graph ===")
        process_knowledge_graph()
        print("\n=== Building Vector Database ===")
        build_vector_db()
        print("\n=== Running Tests ===")
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()