# src/query_interface.py

import argparse
from src.vector_db import KnowledgeGraphVectorDB

def main():
    """Command-line interface for querying the vector database."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Query the knowledge graph vector database')
    parser.add_argument('query', type=str, help='The query text')
    parser.add_argument('--results', type=int, default=3, help='Number of results to return')
    args = parser.parse_args()
    
    # Initialize vector database
    vector_db = KnowledgeGraphVectorDB()
    
    # Check if database is empty
    if vector_db.get_collection_count() == 0:
        print("Error: Vector database is empty. Please run 'python src/vector_db.py' to populate it.")
        return
    
    # Query database
    results = vector_db.query(args.query, n_results=args.results)
    
    # Display results
    print(f"\nQuery: '{args.query}'")
    print(f"Found {len(results['documents'][0])} relevant results:\n")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        relevance = 1 - distance  # Convert distance to relevance score
        print(f"=== Result {i+1} (Relevance: {relevance:.2f}) ===")
        print(f"Title: {metadata['title']}")
        print(f"Severity: {metadata['severity']}")
        print("\nFull Content:")
        print(doc)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()