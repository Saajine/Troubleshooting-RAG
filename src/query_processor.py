# At the top of query_processor.py
import json
import os
import re
from pathlib import Path
import logging
import sys
import time

# Add the parent directory to sys.path to fix imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from src.vector_db import KnowledgeGraphVectorDB
from src.ollama_interface import OllamaInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self, vector_db=None, ollama_interface=None, model_name="llama3"):
        """Initialize query processor."""
        # Initialize vector database
        if vector_db is None:
            self.vector_db = KnowledgeGraphVectorDB()
        else:
            self.vector_db = vector_db
        
        # Initialize Ollama interface
        if ollama_interface is None:
            self.ollama_interface = OllamaInterface(model_name=model_name)
        else:
            self.ollama_interface = ollama_interface
        
        # Create chains
        self.query_chain = self.ollama_interface.create_query_chain()
        self.answer_chain = self.ollama_interface.create_answer_chain()
    
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
        start_time = time.time()
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

            # Get ChromaDB query time
            chroma_time = search_results.get('query_time', 0)
            
            # Step 4: Prepare context for answer generation
            context = self._prepare_context(search_results)
            
            # Step 5: Generate answer
            logger.info("Generating answer")
            answer = self.answer_chain.run(context=context, question=user_question)
            total_time = time.time() - start_time
            
            return {
                'query': user_question,
                'analysis': query_analysis,
                'results': search_results,
                'answer': answer,
                'total_processing_time': total_time,  # Total time from question to answer
                'chroma_query_time': chroma_time
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
            relevance = max(0, 1 - distance) 
            context += f"--- Result {i+1} (Relevance: {relevance:.2f}) ---\n"
            
            # Safely access metadata fields
            title = metadata.get('title', 'No title available')
            severity = metadata.get('severity', 'Not specified')
            
            context += f"Title: {title}\n"
            context += f"Severity: {severity}\n\n"
            context += doc
            context += "\n\n"
    
        return context