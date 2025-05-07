import os
import datetime
from pathlib import Path

def log_response(query, response_data):
    """
    Log the OpenRouter API response to a text file.
    
    Args:
        query (str): The original user query
        response_data (dict): The response data containing 'response' and 'reasoning'
    
    Returns:
        str: Path to the created log file
    """
    # Create log directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate timestamp and filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.txt"
    file_path = log_dir / filename
    
    # Prepare log content
    log_content = [
        f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Query: {query}",
        "Response:",
        response_data.get('response', 'No response'),
    ]
    
    # Add reasoning if available
    if response_data.get('reasoning'):
        log_content.extend([
            "",
            "Reasoning:",
            response_data.get('reasoning')
        ])
    
    # Write to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(log_content))
        return str(file_path)
    except Exception as e:
        print(f"Error writing log file: {e}")
        return None