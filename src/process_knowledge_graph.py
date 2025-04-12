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
        'version': product.get('version'),
        'release_date': product.get('release_date'),  # Added field
        'description': product.get('description')     # Added field
    })
    
    # Extract issues and related entities
    for issue in product.get('issues', []):
        issue_id = issue.get('issue_id')
        issues.append({
            'id': issue_id,
            'product_id': product_id,
            'title': issue.get('title'),
            'description': issue.get('description'),
            'severity': issue.get('severity'),
            'frequency': issue.get('frequency')  # Added field
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
    
    # Create additional entity lists for new elements in the knowledge graph
    diagnostic_tests = []
    log_entries = []
    faqs = []
    user_feedback = []
    
    # Extract additional entities from issues
    for issue in product.get('issues', []):
        issue_id = issue.get('issue_id')
        
        # Extract diagnostic tests
        for test in issue.get('diagnostic_tests', []):
            diagnostic_tests.append({
                'id': test.get('test_id'),
                'issue_id': issue_id,
                'name': test.get('name'),
                'description': test.get('description'),
                'procedure': test.get('procedure')
            })
        
        # Extract log entries
        for log in issue.get('log_entries', []):
            log_entries.append({
                'id': log.get('log_id'),
                'issue_id': issue_id,
                'log_type': log.get('log_type'),
                'message': log.get('message'),
                'timestamp': log.get('timestamp')
            })
        
        # Extract FAQs from issues
        for faq in issue.get('faqs', []):
            faqs.append({
                'id': faq.get('faq_id'),
                'issue_id': issue_id,
                'question': faq.get('question'),
                'answer': faq.get('answer')
            })
        
        # Extract user feedback
        for feedback in issue.get('user_feedback', []):
            user_feedback.append({
                'id': feedback.get('feedback_id'),
                'issue_id': issue_id,
                'rating': feedback.get('rating'),
                'comment': feedback.get('comment'),
                'date': feedback.get('date')
            })
    
    # Extract product-level FAQs
    for faq in product.get('faqs', []):
        faqs.append({
            'id': faq.get('faq_id'),
            'issue_id': None,  # No associated issue
            'question': faq.get('question'),
            'answer': faq.get('answer')
        })
    
    # Create DataFrames
    entities = {
        'products': pd.DataFrame(products),
        'issues': pd.DataFrame(issues),
        'symptoms': pd.DataFrame(symptoms),
        'causes': pd.DataFrame(causes),
        'solutions': pd.DataFrame(solutions),
        'steps': pd.DataFrame(steps),
        'diagnostic_tests': pd.DataFrame(diagnostic_tests) if diagnostic_tests else pd.DataFrame(),
        'log_entries': pd.DataFrame(log_entries) if log_entries else pd.DataFrame(),
        'faqs': pd.DataFrame(faqs) if faqs else pd.DataFrame(),
        'user_feedback': pd.DataFrame(user_feedback) if user_feedback else pd.DataFrame()
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
        related_tests = entities['diagnostic_tests'][entities['diagnostic_tests']['issue_id'] == issue['id']] if not entities['diagnostic_tests'].empty else pd.DataFrame()
        related_logs = entities['log_entries'][entities['log_entries']['issue_id'] == issue['id']] if not entities['log_entries'].empty else pd.DataFrame()
        related_faqs = entities['faqs'][entities['faqs']['issue_id'] == issue['id']] if not entities['faqs'].empty else pd.DataFrame()
        related_feedback = entities['user_feedback'][entities['user_feedback']['issue_id'] == issue['id']] if not entities['user_feedback'].empty else pd.DataFrame()
        
        # Build document text
        doc_text = f"Issue: {issue['title']}\nDescription: {issue['description']}\nSeverity: {issue['severity']}\nFrequency: {issue.get('frequency', 'Not specified')}\n"
        
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
        
        # Add diagnostic tests if available
        if not related_tests.empty:
            doc_text += "\nDiagnostic Tests:\n"
            for _, test in related_tests.iterrows():
                doc_text += f"- {test['name']}: {test['description']}\n  Procedure: {test['procedure']}\n"
        
        # Add log entries if available
        if not related_logs.empty:
            doc_text += "\nLog Entries:\n"
            for _, log in related_logs.iterrows():
                doc_text += f"- [{log['timestamp']}] {log['log_type'].upper()}: {log['message']}\n"
        
        # Add FAQs if available
        if not related_faqs.empty:
            doc_text += "\nFrequently Asked Questions:\n"
            for _, faq in related_faqs.iterrows():
                doc_text += f"- Q: {faq['question']}\n  A: {faq['answer']}\n"
        
        # Add user feedback if available
        if not related_feedback.empty:
            doc_text += "\nUser Feedback:\n"
            for _, feedback in related_feedback.iterrows():
                doc_text += f"- Rating: {feedback['rating']}/5, Date: {feedback['date']}\n  Comment: {feedback['comment']}\n"
        
        # Add document
        documents.append({
            'id': issue['id'],
            'text': doc_text,
            'metadata': {
                'product_id': issue['product_id'] or '',
                'issue_id': issue['id'] or '',
                'title': issue['title'] or '',
                'severity': issue['severity'] or 'Unknown',
                'frequency': issue.get('frequency', 'Not specified')
            }
        })
    
    # Add product-level FAQs as a separate document if there are any
    product_faqs = entities['faqs'][entities['faqs']['issue_id'].isna()] if not entities['faqs'].empty else pd.DataFrame()
    if not product_faqs.empty and not entities['products'].empty:
        product = entities['products'].iloc[0]
        doc_text = f"Product: {product['name']} (Version: {product['version']})\nDescription: {product.get('description', '')}\n\nGeneral Frequently Asked Questions:\n"
        for _, faq in product_faqs.iterrows():
            doc_text += f"- Q: {faq['question']}\n  A: {faq['answer']}\n"
        
        documents.append({
            'id': f"product_faqs_{product['id']}",
            'text': doc_text,
            'metadata': {
                'product_id': product['id'],
                'type': 'product_faqs'
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