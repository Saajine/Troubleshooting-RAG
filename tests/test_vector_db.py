# tests/test_vector_db.py

import unittest
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vector_db import KnowledgeGraphVectorDB

class TestVectorDB(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test database directory using tempfile to avoid permission issues
        self.test_db_dir = tempfile.mkdtemp()
        self.test_collection = "test_collection"
        
        # Initialize the vector database
        self.vector_db = KnowledgeGraphVectorDB(
            collection_name=self.test_collection,
            persist_directory=self.test_db_dir
        )
        
        # Test documents
        self.test_documents = [
            {
                'id': 'test001',
                'text': 'This is a test document about login issues. User cannot login due to timeout.',
                'metadata': {
                    'product_id': 'prod001',
                    'issue_id': 'test001',
                    'title': 'Test Login Issue',
                    'severity': 'High'
                }
            },
            {
                'id': 'test002',
                'text': 'This is a test document about crash issues. Application crashes on startup.',
                'metadata': {
                    'product_id': 'prod001',
                    'issue_id': 'test002',
                    'title': 'Test Crash Issue',
                    'severity': 'Critical'
                }
            }
        ]
        
        # Add test documents
        self.vector_db.add_documents(self.test_documents)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove test database directory
        if os.path.exists(self.test_db_dir):
            shutil.rmtree(self.test_db_dir)
    
    def test_add_documents(self):
        """Test adding documents to the vector database."""
        count = self.vector_db.get_collection_count()
        self.assertEqual(count, 2)
    
    def test_query(self):
        """Test querying the vector database."""
        # Test query related to login
        login_results = self.vector_db.query("login problem")
        self.assertEqual(len(login_results['ids'][0]), 2)  # Should return both documents
        
        # Check that the login document is more relevant
        login_distances = login_results['distances'][0]
        # The first result should be more relevant (smaller distance) for login query
        self.assertLess(login_distances[0], login_distances[1])
        
        # Test query related to crash
        crash_results = self.vector_db.query("application crash")
        self.assertEqual(len(crash_results['ids'][0]), 2)  # Should return both documents
        
        # Check that the crash document is more relevant
        crash_distances = crash_results['distances'][0]
        # The first result should be more relevant (smaller distance) for crash query
        self.assertLess(crash_distances[0], crash_distances[1])

if __name__ == '__main__':
    unittest.main()