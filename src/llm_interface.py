# src/llm_interface.py

import os
from langchain.llms import HuggingFacePipeline, LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMInterface:
    def __init__(self, model_type="huggingface", 
                 model_path="meta-llama/Llama-3-8B-Instruct",
                 device="cpu", max_tokens=1024):
        """Initialize LLM interface."""
        self.model_type = model_type
        self.model_path = model_path
        self.device = device
        self.max_tokens = max_tokens
        self.llm = None
        
        # Initialize LLM
        self._init_llm()
    
    def _init_llm(self):
        """Initialize the language model."""
        try:
            if self.model_type == "huggingface":
                logger.info(f"Initializing Hugging Face model: {self.model_path}")
                
                # Initialize tokenizer and model
                tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    low_cpu_mem_usage=True,
                )
                
                # Create text generation pipeline
                text_generation_pipeline = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=self.max_tokens,
                    temperature=0.1,
                    top_p=0.95,
                    repetition_penalty=1.15
                )
                
                # Create LangChain LLM
                self.llm = HuggingFacePipeline(pipeline=text_generation_pipeline)
                
            elif self.model_type == "llama.cpp":
                logger.info(f"Initializing Llama.cpp model: {self.model_path}")
                
                # Setup callback manager for streaming
                callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
                
                # Create LlamaCpp instance
                self.llm = LlamaCpp(
                    model_path=self.model_path,
                    n_ctx=4096,
                    n_gpu_layers=1 if torch.cuda.is_available() else 0,
                    callback_manager=callback_manager,
                    verbose=True,
                    temperature=0.1,
                    max_tokens=self.max_tokens,
                )
            
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
                
            logger.info("LLM initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise
    
    def create_query_chain(self):
        """Create a chain for query understanding."""
        template = """
        You are an expert in understanding user questions and converting them into structured queries.
        
        Your task is to identify the key entities, relationships, and constraints from the user's question.
        
        The knowledge graph contains information about software products, issues, symptoms, causes, and solutions.
        
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

def main():
    """Test the LLM interface."""
    # Initialize LLM interface
    llm_interface = LLMInterface()
    
    # Create query understanding chain
    query_chain = llm_interface.create_query_chain()
    
    # Test with a sample question
    test_question = "What are the common causes of login failures?"
    result = query_chain.run(question=test_question)
    
    print("\nQuery Analysis Result:")
    print(result)

if __name__ == "__main__":
    main()