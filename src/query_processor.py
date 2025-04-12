# src/query_processor.py

import json
import os
import re
from pathlib import Path
import logging
from vector_db import KnowledgeGraphVectorDB
from llm_interface import LLMInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self, vector_db=None, llm_interface=None):
        """Initialize query processor."""
        # Initialize vector database
        if vector_db is None:
            self.vector_db = KnowledgeGraphVectorDB()
        else:
            self.vector_db = vector_db
        
        # Initialize LLM interface
        if llm_interface is None:
            self.llm_interface = LLMInterface()
        else:
            self.llm_interface = llm_interface
        
        # Create chains
        self.query_chain = self.llm_interface.create_query_chain()
        self.answer_chain = self.llm_interface.create_answer_chain()
    
    def _parse_query_analysis(self, analysis):
        """Parse the LLM's query analysis."""
        # Extract keywords for vector search
        keywords_match = re.search(r'5\.\s*Keywords for vector search[:\s]*(.*?)(?:\n\n|\Z)', analysis, re.DOTALL)
        keywords = keywords_match.group(1).strip() if keywords_match else analysis
        
        # Extract any potential filters
        severity_match = re.search(r'(?:severity|priority)[:\s]*(high|medium|low|critical)', analysis, re.IGNORECASE)
        severity_filter = severity_match.group(1).capitalize() if severity_match else None
        
        return {
            'keywords': keywords,
            'filters': {
                'severity': severity_filter
            }
        }
    
    def process_query(self, user_question, n_results=3):
        """Process a user query and generate an answer."""
        logger.info(f"Processing query: {user_question}")
        
        try:
            # Step 1: Analyze the query with LLM
            logger.info("Analyzing query with LLM")
            query_analysis = self.query_chain.run(question=user_question)
            logger.debug(f"Query analysis: {query_analysis}")
            
            # Step 2: Parse the analysis
            parsed_analysis = self._parse_query_analysis(query_analysis)
            logger.debug(f"Parsed analysis: {parsed_analysis}")
            
            # Step 3: Search the vector database
            logger.info(f"Searching vector database with keywords: {parsed_analysis['keywords']}")
            search_results = self.vector_db.query(parsed_analysis['keywords'], n_results=n_results)
            
            # Step 4: Prepare context for answer generation
            context = self._prepare_context(search_results)
            
            # Step 5: Generate answer
            logger.info("Generating answer")
            answer = self.answer_chain.run(context=context, question=user_question)
            
            return {
                'query': user_question,
                'analysis': query_analysis,
                'results': search_results,
                'answer': answer
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'query': user_question,
                'error': str(e)
            }
    
    def _prepare_context(self, search_results):
        """Prepare context from search results for the LLM."""
        context = "Here's information from our knowledge base:\n\n"
        
        # Check if there are any results
        if not search_results or not search_results.get('documents') or len(search_results['documents'][0]) == 0:
            return "No relevant information found in the knowledge base."
        
        # Add each result to the context
        for i, (doc, metadata, distance) in enumerate(zip(
            search_results['documents'][0], 
            search_results['metadatas'][0], 
            search_results['distances'][0]
        )):
            relevance = 1 - distance
            context += f"--- Result {i+1} (Relevance: {relevance:.2f}) ---\n"
            context += f"Title: {metadata['title']}\n"
            context += f"Severity: {metadata['severity']}\n\n"
            context += doc
            context += "\n\n"
        
        return context

def main():
    """Test the query processor."""
    # Initialize query processor
    processor = QueryProcessor()
    
    # Test with a sample question
    test_question = "How do I fix a login failure?"
    result = processor.process_query(test_question)
    
    print("\nQuery Processing Result:")
    print(f"Question: {result['query']}")
    print(f"Answer: {result['answer']}")

if __name__ == "__main__":
    main()