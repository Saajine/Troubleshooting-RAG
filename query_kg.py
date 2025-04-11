from load_graph import load_knowledge_graph

# loading KG globally
KNOWLEDGE_GRAPH = load_knowledge_graph('knowledge_graph.json')

#search for issues in the kg based on query
def query_knowledge_graph(query: str) -> str:
    query_lower = query.lower()
    results = []
    issues = KNOWLEDGE_GRAPH.get("SoftwareProduct", {}).get("issues", [])
    
    for issue in issues:
        title = issue.get("title", "").lower()
        description = issue.get("description", "").lower()
        if query_lower in title or query_lower in description:
            output = f"Issue: {issue.get('title')}\n"
            output += f"Description: {issue.get('description')}\n"
            output += f"Severity: {issue.get('severity')}\n"
            
            for solution in issue.get("solutions", []):
                output += f"\nSolution: {solution.get('description')}\n"
                output += f"Estimated Resolution Time: {solution.get('estimated_resolution_time')}\n"
                output += "Steps:\n"
                
                for step in sorted(solution.get("steps", []), key=lambda x: x.get("sequence", 0)):
                    output += f" Step {step.get('sequence')}: {step.get('instruction')}\n"
            
            results.append(output)
    
    return "\n\n".join(results) if results else "No matching issues found."

if __name__ == "__main__":
    # Test your query function
    test_query = "login failure"
    print(query_knowledge_graph(test_query))