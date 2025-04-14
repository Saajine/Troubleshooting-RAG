// web/static/js/app.js

// Main Knowledge Graph Query Application
const KnowledgeGraphApp = () => {
    const [question, setQuestion] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(false);
    const [result, setResult] = React.useState(null);
    const [error, setError] = React.useState(null);
  
    // Handle form submission
    const handleSubmit = async (e) => {
      e.preventDefault();
      
      // Validate input
      if (!question.trim()) {
        setError('Please enter a question');
        return;
      }
      
      // Reset states
      setIsLoading(true);
      setError(null);
      setResult(null);
      
      try {
        // Send request to API
        const response = await fetch('/api/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question }),
        });
        
        // Parse response
        const data = await response.json();
        
        // Handle errors
        if (!response.ok) {
          throw new Error(data.error || 'An unexpected error occurred');
        }
        
        // Set result
        setResult(data);
      } catch (err) {
        setError(err.message || 'Failed to process query');
      } finally {
        setIsLoading(false);
      }
    };
  
    return (
      <div className="app-container">
        <header className="header">
          <h1>Dassault Software Troubleshooting System</h1>
          <p>Ask questions about software issues, symptoms, causes, and solutions</p>
        </header>
        
        <main className="main-content">
          <form className="query-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="question">Enter your question:</label>
              <textarea
                id="question"
                rows="3"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., having slow performance issue, what to do?"
                disabled={isLoading}
                className="question-input"
              />
            </div>
            
            <button 
              type="submit" 
              className={`submit-button ${isLoading ? 'submit-button-loading' : ''}`}
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : 'Submit Question'}
            </button>
          </form>
          
          {error && (
            <div className="error-message">
              <p>{error}</p>
            </div>
          )}
          
          {result && (
            <div className="result-section">
              <h2>Answer:</h2>
              <div className="answer-container">
                {result.answer}
              </div>
              <div className="timing-info">
                {result.total_processing_time && (
                  <div>Total processing time: {result.total_processing_time.toFixed(2)} seconds</div>
                )}
                {result.chroma_query_time && (
                  <div>ChromaDB query time: {result.chroma_query_time.toFixed(2)} seconds</div>
                )}
              </div>
            </div>
          )}
        </main>
        
        <footer className="footer">
          <p>Powered by ChromaDB with Llama3</p>
        </footer>
      </div>
    );
  };
  
  // Render the application
  ReactDOM.render(<KnowledgeGraphApp />, document.getElementById('app'));


  //-python -m src.main web --port 8080