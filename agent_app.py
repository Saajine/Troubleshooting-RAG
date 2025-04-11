from langchain_community.llms import Ollama 
from langchain.agents import initialize_agent, AgentType, Tool
from query_kg import query_knowledge_graph

#query function wrapped as a LangChain tool
query_tool = Tool(
    name="QueryKnowledgeGraph",
    func=lambda query: query_knowledge_graph(query),
    description=(
        "Queries the troubleshooting knowledge graph and returns details about issues, "
        "solutions, and step-by-step instructions based on the user input."
    )
)

# Initialize Llama via Ollama
llm = Ollama(  
    model="llama3",
    temperature=0
)

#create LangChain agent with our custom tool
agent = initialize_agent(
    tools=[query_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

if __name__ == "__main__":
    user_query = input("Enter your troubleshooting question: ")
    
    response = agent.invoke({"input": user_query})
    
    print("\nAgent Response:\n", response["output"])