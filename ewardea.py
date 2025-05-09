import requests
import json
import urllib3
import sys

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def post_text_to_url(file_path, prompt_path, url):
    """
    Reads a prompt from a file, appends text from another file, escapes JSON special characters, 
    and sends it as a POST request to a specified URL, ignoring SSL certificate errors.

    Parameters:
        file_path (str): The path to the file containing the text.
        prompt_path (str): The path to the file containing the prompt.
        url (str): The URL to which the POST request will be sent.
    """
    try:
        # Read the prompt from the prompt file
        with open(prompt_path, 'r', encoding='utf-8') as prompt_file:
            prompt = prompt_file.read()

        # Read the content of the text file
        with open(file_path, 'r', encoding='utf-8') as text_file:
            text = text_file.read()

        # Combine the prompt and the text
        text = prompt + text

        # Escape JSON special characters
        escaped_text = json.dumps(text)

        # Prepend and append the required text
        escaped_text = f'{{"message": {escaped_text},"mode": "chat"}}'

        # Define headers for the POST request
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX",
            "Content-Type": "application/json"
        }

        # Send the POST request, ignoring SSL certificate errors
        response = requests.post(url, data=escaped_text, headers=headers, verify=False)

        # Check the response status code
        if response.status_code == 200:
            data = response.json()
            print(data['textResponse'])  # Unescape the string
        else:
            print("")  # Print an empty string if the status code is not 200

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the POST request: {e}")

# Example usage
if __name__ == "__main__":
    # Check if the file path and prompt path are provided as command-line arguments
    if len(sys.argv) < 3:
        print("Usage: python ewardea.py <file_path> <prompt_path>")
        sys.exit(1)

    # Get the file path and prompt path from the command-line arguments
    file_path = sys.argv[1]
    prompt_path = sys.argv[2]

    # Replace with the target URL
    url = "https://ai.example.com:3001/api/v1/workspace/tony-micelli/chat"

    post_text_to_url(file_path, prompt_path, url)
