import requests
import json

# Define the base URL where your FastAPI application is running
base_url = "http://0.0.0.0:8000"

# Define the headers for a JSON post request
headers = {
    "Content-Type": "application/json",
}


sample_prompt = {
    "message": "Bob: Write code to sort a list in C++",
    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1", # Replace with your desired model
    "use_openai": False  # Set to False to use Anyscale
}
# Test the /prompt endpoint
def test_prompt():
    response = requests.post(f"{base_url}/prompt", headers=headers, data=json.dumps(sample_prompt))
    if response.status_code == 200:
        print("Prompt Response:", response.json())
    else:
        print("Failed to get response from /prompt endpoint. Status Code:", response.status_code)

# Test the /prompt/stream endpoint
def test_prompt_stream():
    with requests.post(f"{base_url}/prompt/stream", headers=headers, data=json.dumps(sample_prompt), stream=True) as response:
        if response.status_code == 200:
            print("Streamed Responses:")
            try:
                buffer = ''
                for chunk in response.iter_content(chunk_size=1):  # Read one byte at a time
                    if chunk:
                        character = chunk.decode('utf-8')
                        buffer += character
                        if character in ['\n', '.', '?', '!']:  # Flush on certain punctuation or newlines
                            print(buffer)
                            buffer = ''
            except KeyboardInterrupt:
                print("Stream stopped.")
        else:
            print("Failed to get response from /prompt/stream endpoint. Status Code:", response.status_code)




if __name__ == "__main__":
    print("Testing /prompt endpoint...")
    test_prompt()
    print("\nTesting /prompt/stream endpoint...")
    test_prompt_stream()
