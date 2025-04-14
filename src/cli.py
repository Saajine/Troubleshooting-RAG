# src/cli.py

import argparse
import sys
import os
from pathlib import Path
from vector_db import KnowledgeGraphVectorDB
from query_processor import QueryProcessor
from llm_interface import LLMInterface
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_argparse():
    """Set up argument parser."""
    parser = argparse.ArgumentParser(description='Knowledge Graph Query System')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the knowledge graph')
    query_parser.add_argument('question', help='User question')
    query_parser.add_argument('--results', type=int, default=3, help='Number of results to return')
    query_parser.add_argument('--model', choices=['huggingface', 'llama.cpp'], default='huggingface', 
                              help='LLM model type')
    query_parser.add_argument('--model-path', default='meta-llama/Llama-3-8B-Instruct', 
                              help='Path to the model')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive mode')
    interactive_parser.add_argument('--results', type=int, default=3, 
                                   help='Number of results to return')
    interactive_parser.add_argument('--model', choices=['huggingface', 'llama.cpp'], default='huggingface', 
                                   help='LLM model type')
    interactive_parser.add_argument('--model-path', default='meta-llama/Llama-3-8B-Instruct', 
                                   help='Path to the model')
    
    return parser


def interactive_mode(args):
    """Start interactive mode."""
    print("\n" + "="*50)
    print("Knowledge Graph Query System - Interactive Mode")
    print("Type 'exit' or 'quit' to exit")
    print("="*50 + "\n")
    
    # Initialize components
    llm_interface = LLMInterface(model_type=args.model, model_path=args.model_path)
    vector_db = KnowledgeGraphVectorDB()
    processor = QueryProcessor(vector_db=vector_db, llm_interface=llm_interface)
    
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
        result = processor.process_query(user_question, n_results=args.results)
        
        # Print answer
        print("\n" + "-"*50)
        print(f"Answer: {result['answer']}")
        print("-"*50)

def main():
    """Main entry point."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if args.command == 'interactive':
        interactive_mode(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()