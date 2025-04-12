# src/vector_db.py

import json
import os
import chromadb
from pathlib import Path
from chromadb.utils import embedding_functions

class KnowledgeGraphVectorDB:
    def __init__(self, collection_name="knowledge_graph", persist_directory="chroma_db"):
        """Initialize the vector database."""
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Create a persistent client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use sentence-transformers for embeddings
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name, embedding_function=self.embedding_function)
            print(f"Using existing collection '{collection_name}'")
        except Exception as e:
            print(f"Creating new collection '{collection_name}'")
            try:
                self.collection = self.client.create_collection(
                    name=collection_name, 
                    embedding_function=self.embedding_function
                )
            except Exception as create_error:
                print(f"Error creating collection: {create_error}")
                raise
    
    def load_documents(self, file_path):
        """Load processed documents from a JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def add_documents(self, documents):
        """Add documents to the vector database."""
        # Prepare data for bulk insertion
        ids = [doc['id'] for doc in documents]
        texts = [doc['text'] for doc in documents]
        
        # Clean metadata by removing None values
        cleaned_metadatas = []
        for doc in documents:
            # Filter out None values from metadata
            cleaned_metadata = {}
            for key, value in doc['metadata'].items():
                if value is not None:  # Only include non-None values
                    cleaned_metadata[key] = value
            cleaned_metadatas.append(cleaned_metadata)
        
        # Add documents to collection
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=cleaned_metadatas
        )
        print(f"Added {len(documents)} documents to the collection")
    
    def query(self, query_text, n_results=3):
        """Query the vector database."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
    
    def get_collection_count(self):
        """Get the number of documents in the collection."""
        return self.collection.count()

def main():
    """Main function to build the vector database."""
    # Define paths
    processed_data_path = Path('data/processed/documents.json')
    
    # Initialize vector database
    vector_db = KnowledgeGraphVectorDB()
    
    # Load processed documents
    documents = vector_db.load_documents(processed_data_path)
    
    # Add documents to vector database
    vector_db.add_documents(documents)
    
    # Print collection count
    print(f"Total documents in collection: {vector_db.get_collection_count()}")


if __name__ == "__main__":
    main()