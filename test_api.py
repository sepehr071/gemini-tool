import requests

def test_api():
    """
    Test the OpenRouter Flask API by sending a request to the /generate endpoint.
    """
    # API endpoint
    url = "http://localhost:5000/generate"
    
    # Test data
    data = {
        "text": "Which device has the highest battery capacity?"
    }
    
    # Send POST request
    try:
        response = requests.post(url, json=data)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            
            # Display reasoning if available
            if result.get('reasoning'):
                print("\n--- MODEL REASONING ---")
                print(result['reasoning'])
                print("\n--- FINAL RESPONSE ---")
            
            print(f"Response: {result['response']}")
        else:
            print(f"Request failed with status code {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    print("Testing the OpenRouter Flask API...")
    test_api()