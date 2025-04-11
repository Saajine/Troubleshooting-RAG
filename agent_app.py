from langchain_community.llms import Ollama 
from langchain.agents import initialize_agent, AgentType, Tool
from query_kg import query_knowledge_graph

# wrapping the query function as langChain tool
query_tool = Tool(
    name="QueryKnowledgeGraph",
    func=lambda query: query_knowledge_graph(query),
    description=(
        "Queries the troubleshooting knowledge graph and returns details about issues, "
        "solutions, and step-by-step instructions based on the user input."
    )
)

# initializimg ilama via ollama
llm = Ollama(
    model="llama3", 
    temperature=0
)

# creating langChain agent
agent = initialize_agent(
    tools=[query_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True 
)

if __name__ == "__main__":
    user_query = "How to fix a login failure?"
    response = agent.run(user_query)
    print("Agent Response:\n", response)