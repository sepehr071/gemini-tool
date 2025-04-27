import requests
import os
import pathlib

def load_product_info():
    """
    Load product information from product-infotxt.txt file.
    
    Returns:
        str: Content of the product info file
    """
    try:
        # Get the directory where the script is located
        script_dir = pathlib.Path(__file__).parent.parent.absolute()
        file_path = script_dir / 'product-infotxt.txt'
        
        print(f"Attempting to load product info from: {file_path}")
        
        if not file_path.exists():
            print(f"WARNING: Product info file not found at {file_path}")
            
            # Try absolute path as fallback
            absolute_path = pathlib.Path('c:/Users/USer/Desktop/fresh-livekit/product-infotxt.txt')
            if absolute_path.exists():
                print(f"Found product info at absolute path: {absolute_path}")
                file_path = absolute_path
            else:
                print(f"WARNING: Product info also not found at absolute path: {absolute_path}")
                return "Product information not found. Please ensure product-infotxt.txt exists."
        
        # Try multiple encodings since there's a character encoding issue
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        # Try to read file with specific error handling for problematic bytes
        try:
            # Open in binary mode first to handle encoding issues
            with open(file_path, 'rb') as file:
                raw_content = file.read()
                
            # Replace problematic byte with a space
            cleaned_content = raw_content.replace(b'\x81', b' ')
            
            # Decode with utf-8 after cleaning
            content = cleaned_content.decode('utf-8', errors='replace')
            
            if content:
                print(f"Successfully loaded product info with custom handling ({len(content)} characters)")
                return content
            else:
                print("WARNING: Product info file is empty")
                return "Product information file is empty."
                
        except Exception as e:
            print(f"ERROR loading product info with custom handling: {str(e)}")
            import traceback
            traceback.print_exc()
            return "Product information unavailable due to error: " + str(e)
    except Exception as e:
        print(f"ERROR loading product info: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Product information unavailable due to error: " + str(e)

def generate_completion(user_input, system_prompt):
    """
    Send a completion request to OpenRouter API using the google/gemini-2.5-pro-preview-03-25 model.
    
    Args:
        user_input (str): The text input from the user
        system_prompt (str): The system prompt loaded from YAML config
        
    Returns:
        str: The text response from the model
        
    Raises:
        ValueError: If API key is not found
        Exception: If API request fails
    """
    # Base system prompt optimized for product information responses
    base_system_prompt = """You are a knowledgeable assistant focused solely on providing accurate product information.
- Only answer questions based on the specific product information provided
- Keep responses concise and factual
- If information is not available in the product data, politely indicate this
- Do not make up or infer information that isn't explicitly stated
- Do not discuss topics unrelated to the product
- Format technical specifications clearly using bullet points where appropriate
- Use a professional, helpful tone

PRODUCT INFORMATION:
"""
    
    # Load system prompt only - product info will be added to user message
    combined_prompt = f"{base_system_prompt}\n{system_prompt}"
    
    # Load product info from file and append to user message
    product_info = load_product_info()
    enhanced_user_input = f"Here is the product information:\n\n{product_info}\n\nBased on this product information, please answer: {user_input}"
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OpenRouter API key not found in environment variables")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:5000",  # For personal use
        "X-Title": "OpenRouter Flask API"
    }
    
    data = {
        "model": "google/gemini-2.5-flash-preview:thinking",
        "temperature": 0.1,
        # "reasoning": {
        #     "max_tokens": 1000,
        #     "exclude": True
        # },
        "messages": [
            {
                "role": "system",
                "content": combined_prompt
            },
            {
                "role": "user",
                "content": enhanced_user_input
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        response_data = response.json()
        
        # Check if reasoning is included in the response
        message = response_data['choices'][0]['message']
        if 'reasoning' in message and message['reasoning']:
            # Return both reasoning and content
            return {
                'response': message['content'],
                'reasoning': message['reasoning']
            }
        else:
            # Return just the content if no reasoning
            return {
                'response': message['content'],
                'reasoning': None
            }
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_msg = f"API request failed with status code {e.response.status_code}: {e.response.text}"
        else:
            error_msg = f"API request failed: {str(e)}"
        raise Exception(error_msg)