# tests/test_knowledge_graph.py

import unittest
import json
import os
from pathlib import Path
import sys

# Add src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.process_knowledge_graph import load_knowledge_graph, extract_entities_and_relationships, create_documents_for_vectorization

class TestKnowledgeGraph(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_path = Path('data/raw/knowledge_graph.json')
        self.knowledge_graph = load_knowledge_graph(self.test_data_path)
        self.entities = extract_entities_and_relationships(self.knowledge_graph)
        self.documents = create_documents_for_vectorization(self.entities)
    
    def test_load_knowledge_graph(self):
        """Test loading the knowledge graph."""
        self.assertIsNotNone(self.knowledge_graph)
        self.assertIn('SoftwareProduct', self.knowledge_graph)
    
    def test_extract_entities(self):
        """Test extracting entities from the knowledge graph."""
        self.assertIn('products', self.entities)
        self.assertIn('issues', self.entities)
        self.assertIn('symptoms', self.entities)
        self.assertIn('causes', self.entities)
        self.assertIn('solutions', self.entities)
        self.assertIn('steps', self.entities)
        
        # Check that we have the expected number of entities
        self.assertEqual(len(self.entities['products']), 1)
        self.assertEqual(len(self.entities['issues']), 2)
    
    def test_create_documents(self):
        """Test creating documents for vectorization."""
        self.assertEqual(len(self.documents), 2)  # Should have one document per issue
        
        # Check document structure
        for doc in self.documents:
            self.assertIn('id', doc)
            self.assertIn('text', doc)
            self.assertIn('metadata', doc)
            
            # Check metadata
            self.assertIn('product_id', doc['metadata'])
            self.assertIn('issue_id', doc['metadata'])
            self.assertIn('title', doc['metadata'])
            self.assertIn('severity', doc['metadata'])

if __name__ == '__main__':
    unittest.main()