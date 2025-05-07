from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from utils.openrouter import generate_completion
from utils.logger import log_response

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app)

def get_default_system_prompt():
    """Return a default system prompt"""
    return "You are a helpful assistant that provides accurate information about products based on the provided data."

@app.route('/generate', methods=['POST'])
def generate():
    """
    Endpoint to generate text completions using OpenRouter and Gemini model.
    
    Expects a JSON payload with a 'text' field.
    Returns a JSON response with the model's output.
    """
    # Get JSON data from request
    data = request.get_json()
    
    # Validate input
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing required field: text'}), 400
    
    # Get user input
    user_input = data.get('text', '')
    
    # Validate that text is not empty
    if not user_input.strip():
        return jsonify({'error': 'Text field cannot be empty'}), 400
    
    # Get default system prompt
    system_prompt = get_default_system_prompt()
    
    try:
        # Call OpenRouter API
        result = generate_completion(user_input, system_prompt)
        
        # Log the response to a file
        log_file = log_response(user_input, result)
        if log_file:
            app.logger.info(f"Response logged to {log_file}")
        
        return jsonify({
            'response': result['response'],
            'reasoning': result['reasoning']
        })
    except ValueError as e:
        # For configuration errors (like missing API key)
        app.logger.error(f"Configuration error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        # For API request errors or other issues
        app.logger.error(f"Error generating completion: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Get configuration from environment variables with defaults
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5100))
    
    # Run the Flask app - host='0.0.0.0' makes it accessible from any IP
    app.run(debug=debug_mode, host='0.0.0.0', port=port)