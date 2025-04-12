# tests/test_query_processor.py

import unittest
import os
import sys
from pathlib import Path
import json
from unittest.mock import MagicMock, patch

# Add src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.query_processor import QueryProcessor

class TestQueryProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock LLM interface
        self.mock_llm_interface = MagicMock()
        self.mock_query_chain = MagicMock()
        self.mock_answer_chain = MagicMock()
        self.mock_llm_interface.create_query_chain.return_value = self.mock_query_chain
        self.mock_llm_interface.create_answer_chain.return_value = self.mock_answer_chain
        
        # Create mock vector DB
        self.mock_vector_db = MagicMock()
        
        # Create query processor with mocks
        self.processor = QueryProcessor(
            vector_db=self.mock_vector_db,
            llm_interface=self.mock_llm_interface
        )
    
    def test_parse_query_analysis(self):
        """Test parsing of query analysis."""
        test_analysis = """
        1. Key entities mentioned: Login, credentials
        2. Relationships of interest: Login failure
        3. Constraints or filters: None
        4. A suggested query strategy: Search for login-related issues
        5. Keywords for vector search: login failure credentials
        """
        
        parsed = self.processor._parse_query_analysis(test_analysis)
        self.assertEqual(parsed['keywords'], "login failure credentials")
        self.assertIsNone(parsed['filters']['severity'])
        
        # Test with severity filter
        test_analysis_with_severity = """
        1. Key entities mentioned: Login, credentials
        2. Relationships of interest: Login failure
        3. Constraints or filters: Severity: High
        4. A suggested query strategy: Search for high severity login-related issues
        5. Keywords for vector search: login failure credentials high severity
        """
        
        parsed = self.processor._parse_query_analysis(test_analysis_with_severity)
        self.assertEqual(parsed['keywords'], "login failure credentials high severity")
        self.assertEqual(parsed['filters']['severity'], "High")
    
    def test_process_query(self):
        """Test query processing."""
        # Setup mock returns
        self.mock_query_chain.run.return_value = """
        1. Key entities mentioned: Login, credentials
        2. Relationships of interest: Login failure
        3. Constraints or filters: None
        4. A suggested query strategy: Search for login-related issues
        5. Keywords for vector search: login failure credentials
        """
        
        self.mock_vector_db.query.return_value = {
            'documents': [["This is a test document about login issues"]],
            'metadatas': [[{'title': 'Login Failure', 'severity': 'High'}]],
            'distances': [[0.1]],
            'ids': [["test001"]]
        }
        
        self.mock_answer_chain.run.return_value = "To fix a login failure, check your credentials and network connection."
        
        # Call method under test
        result = self.processor.process_query("How do I fix a login failure?")
        
        # Assertions
        self.assertEqual(result['query'], "How do I fix a login failure?")
        self.assertEqual(result['answer'], "To fix a login failure, check your credentials and network connection.")
        self.mock_query_chain.run.assert_called_once()
        self.mock_vector_db.query.assert_called_once()
        self.mock_answer_chain.run.assert_called_once()

if __name__ == '__main__':
    unittest.main()