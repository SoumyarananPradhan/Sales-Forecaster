import requests

# The URL of your API endpoint
url = 'http://127.0.0.1:8000/api/analyze/'

# Open the dummy CSV file
with open('data.csv', 'rb') as f:
    # --- FIX IS HERE: Change 'file' to 'csv_file' ---
    files = {'csv_file': f} 
    
    print("Sending request to server...")
    
    try:
        response = requests.post(url, files=files)
        
        # Print the result
        if response.status_code == 201:
            print("SUCCESS! Server Response:")
            print(response.json())
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")