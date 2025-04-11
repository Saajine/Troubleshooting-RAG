import json

def load_knowledge_graph(filepath):
    #load JSON file, return content as python dict
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return None
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON file.")
        return None

if __name__ == "__main__":
    #set file path to JSON file
    filepath = 'knowledge_graph.json'
    knowledge_graph = load_knowledge_graph(filepath)
    if knowledge_graph:
        product_name = knowledge_graph.get("SoftwareProduct", {}).get("name")
        print("Product Name:", product_name)
        # print(json.dumps(knowledge_graph, indent=4))