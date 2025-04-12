# src/process_knowledge_graph.py

import json
import pandas as pd
from pathlib import Path

def load_knowledge_graph(file_path):
    """Load the knowledge graph from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_entities_and_relationships(knowledge_graph):
    """Extract entities and relationships from the knowledge graph."""
    
    # Initialize lists to store entities
    products = []
    issues = []
    symptoms = []
    causes = []
    solutions = []
    steps = []
    
    # Extract product information
    product = knowledge_graph.get('SoftwareProduct', {})
    product_id = product.get('product_id')
    products.append({
        'id': product_id,
        'name': product.get('name'),
        'version': product.get('version')
    })
    
    # Extract issues and related entities
    for issue in product.get('issues', []):
        issue_id = issue.get('issue_id')
        issues.append({
            'id': issue_id,
            'product_id': product_id,
            'title': issue.get('title'),
            'description': issue.get('description'),
            'severity': issue.get('severity')
        })
        
        # Extract symptoms
        for symptom in issue.get('symptoms', []):
            symptoms.append({
                'id': symptom.get('symptom_id'),
                'issue_id': issue_id,
                'description': symptom.get('description')
            })
        
        # Extract causes
        for cause in issue.get('causes', []):
            causes.append({
                'id': cause.get('cause_id'),
                'issue_id': issue_id,
                'description': cause.get('description')
            })
        
        # Extract solutions
        for solution in issue.get('solutions', []):
            solution_id = solution.get('solution_id')
            solutions.append({
                'id': solution_id,
                'issue_id': issue_id,
                'description': solution.get('description'),
                'estimated_resolution_time': solution.get('estimated_resolution_time')
            })
            
            # Extract steps
            for step in solution.get('steps', []):
                steps.append({
                    'id': step.get('step_id'),
                    'solution_id': solution_id,
                    'sequence': step.get('sequence'),
                    'instruction': step.get('instruction')
                })
    
    # Create DataFrames
    entities = {
        'products': pd.DataFrame(products),
        'issues': pd.DataFrame(issues),
        'symptoms': pd.DataFrame(symptoms),
        'causes': pd.DataFrame(causes),
        'solutions': pd.DataFrame(solutions),
        'steps': pd.DataFrame(steps)
    }
    
    return entities

def create_documents_for_vectorization(entities):
    """Create documents suitable for vectorization."""
    documents = []
    
    # Create documents for issues
    for _, issue in entities['issues'].iterrows():
        # Get related entities
        related_symptoms = entities['symptoms'][entities['symptoms']['issue_id'] == issue['id']]
        related_causes = entities['causes'][entities['causes']['issue_id'] == issue['id']]
        related_solutions = entities['solutions'][entities['solutions']['issue_id'] == issue['id']]
        
        # Build document text
        doc_text = f"Issue: {issue['title']}\nDescription: {issue['description']}\nSeverity: {issue['severity']}\n"
        
        # Add symptoms
        doc_text += "\nSymptoms:\n"
        for _, symptom in related_symptoms.iterrows():
            doc_text += f"- {symptom['description']}\n"
        
        # Add causes
        doc_text += "\nCauses:\n"
        for _, cause in related_causes.iterrows():
            doc_text += f"- {cause['description']}\n"
        
        # Add solutions
        doc_text += "\nSolutions:\n"
        for _, solution in related_solutions.iterrows():
            doc_text += f"- {solution['description']} (Est. time: {solution['estimated_resolution_time']})\n"
            
            # Add steps
            related_steps = entities['steps'][entities['steps']['solution_id'] == solution['id']].sort_values('sequence')
            doc_text += "  Steps:\n"
            for _, step in related_steps.iterrows():
                doc_text += f"  {step['sequence']}. {step['instruction']}\n"
        
        # Add document
        documents.append({
            'id': issue['id'],
            'text': doc_text,
            'metadata': {
                'product_id': issue['product_id'],
                'issue_id': issue['id'],
                'title': issue['title'],
                'severity': issue['severity']
            }
        })
    
    return documents

def main():
    """Main function to process the knowledge graph."""
    # Define paths
    raw_data_path = Path('data/raw/knowledge_graph.json')
    processed_data_path = Path('data/processed/documents.json')
    
    # Load knowledge graph
    knowledge_graph = load_knowledge_graph(raw_data_path)
    
    # Extract entities and relationships
    entities = extract_entities_and_relationships(knowledge_graph)
    
    # Create documents for vectorization
    documents = create_documents_for_vectorization(entities)
    
    # Save processed data
    processed_data_path.parent.mkdir(exist_ok=True)
    with open(processed_data_path, 'w') as f:
        json.dump(documents, f, indent=2)
    
    print(f"Processed {len(documents)} documents and saved to {processed_data_path}")

if __name__ == "__main__":
    main()