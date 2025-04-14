# src/ollama_interface.py

import requests
import json
import logging
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, List, Optional, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaLLM(LLM):
    """LangChain integration for Ollama"""
    
    model_name: str = "llama3"
    temperature: float = 0.1
    base_url: str = "http://localhost:11434"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Ollama API."""
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False
        }
        
        if stop:
            data["stop"] = stop
            
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "ollama"

class OllamaInterface:
    def __init__(self, model_name="llama3", temperature=0.1):
        """Initialize Ollama interface."""
        self.model_name = model_name
        self.temperature = temperature
        logger.info(f"Initializing Ollama with model: {model_name}")
        try:
            self.llm = OllamaLLM(model_name=model_name, temperature=temperature)
            logger.info("Ollama initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Ollama: {e}")
            raise
    
    def create_query_chain(self):
        """Create a chain for query understanding."""
        template = """
        You are an expert in understanding user questions and converting them into structured queries.
        
        Your task is to identify the key entities, relationships, and constraints from the user's question.
        
        The knowledge graph contains information about software products, issues, symptoms, causes, and solutions, faqs, severity, test/log, steps, user feedback.
        
        User Question: {question}
        
        Please analyze this question and provide the following:
        
        1. Key entities mentioned (products, issues, symptoms, causes, solutions)
        2. Relationships of interest
        3. Constraints or filters
        4. A suggested query strategy
        5. Keywords for vector search
        
        Format your response in a structured way that can be parsed.
        """
        
        prompt = PromptTemplate(template=template, input_variables=["question"])
        return LLMChain(prompt=prompt, llm=self.llm)
    
    def create_answer_chain(self):
        """Create a chain for answer generation."""
        template = """
        You are a helpful assistant that provides accurate information based on the given context.
        
        Context information:
        {context}
        
        User Question: {question}
        
        Provide a clear, concise answer using ONLY the information in the context above.
        If the context doesn't contain enough information to answer the question, say so clearly.
        Do not make up or hallucinate any information not present in the context.
        
        Answer:
        """
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        return LLMChain(prompt=prompt, llm=self.llm)