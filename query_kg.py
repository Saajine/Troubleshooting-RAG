from load_graph import load_knowledge_graph
from thefuzz import fuzz

# loading KG globally
KNOWLEDGE_GRAPH = load_knowledge_graph('knowledge_graph.json')


def query_knowledge_graph(query: str) -> str:
    query_lower = query.lower()
    results = []
    issues = KNOWLEDGE_GRAPH.get("SoftwareProduct", {}).get("issues", [])
    
    for issue in issues:
        title = issue.get("title", "").lower()
        description = issue.get("description", "").lower()
        # similarity score between query and title
        similarity = fuzz.partial_ratio(query_lower, title)
        if similarity > 70 or query_lower in description:  
            result_text = f"Issue: {issue.get('title')}\n"
            result_text += f"Description: {issue.get('description')}\n"
            result_text += f"Severity: {issue.get('severity')}\n"
            for solution in issue.get("solutions", []):
                result_text += f"\nSolution: {solution.get('description')}\n"
                result_text += f"Estimated Resolution Time: {solution.get('estimated_resolution_time')}\n"
                result_text += "Steps:\n"
                for step in sorted(solution.get("steps", []), key=lambda x: x.get("sequence", 0)):
                    result_text += f"  Step {step.get('sequence')}: {step.get('instruction')}\n"
            results.append(result_text)
    
    return "\n\n".join(results) if results else "No matching issues found."




