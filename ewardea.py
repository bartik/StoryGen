import sys
import requests
import urllib3
import argparse
import configparser
import logging

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_configuration(args):
    """
    Load configuration from a file and override with command-line arguments.

    Parameters:
        args (Namespace): Parsed command-line arguments.

    Returns:
        dict: A dictionary containing the final configuration values.
    """
    config = configparser.ConfigParser()
    if args.config:
        try:
            config.read(args.config)
            if not config.sections() and not config.defaults():
                raise ValueError(f"Configuration file '{args.config}' is empty or invalid.")
        except Exception as e:
            logging.error(f"Error reading configuration file: {e}")
            raise

    # Determine the section to read from
    section = args.section if args.section else "DEFAULT"

    # Load and override configuration
    return {
        "file_path": args.file or config.get(section, "file", fallback=None),
        "prompt_path": args.prompt or config.get(section, "prompt", fallback=None),
        "url": args.url or config.get(section, "url", fallback=None),
        "bearer_token": args.bearer or config.get(section, "bearer", fallback=None),
    }

def validate_configuration(config):
    """
    Validate the configuration to ensure all required parameters are provided.

    Parameters:
        config (dict): Configuration dictionary.

    Raises:
        ValueError: If any required parameter is missing.
    """
    required_keys = ["file_path", "prompt_path", "url", "bearer_token"]
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        logging.error(f"Missing required parameters: {', '.join(missing_keys)}")
        raise ValueError(f"Missing required parameters: {', '.join(missing_keys)}")

def prepare_headers(bearer_token):
    """
    Prepare headers for the POST request.

    Parameters:
        bearer_token (str): The Bearer token for authorization.

    Returns:
        dict: A dictionary of headers.
    """
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

def post_text_to_url(file_path, prompt_path, url, headers):
    """
    Reads a prompt from a file, appends text from another file, escapes JSON special characters, 
    and sends it as a POST request to a specified URL, ignoring SSL certificate errors.

    Parameters:
        file_path (str): The path to the file containing the text.
        prompt_path (str): The path to the file containing the prompt.
        url (str): The URL to which the POST request will be sent.
        headers (dict): Headers for the POST request.

    Returns:
        str: The response text from the server.
    """
    try:
        # Read the prompt from the prompt file
        with open(prompt_path, 'r') as prompt_file:
            prompt = prompt_file.read()

        # Read the content of the text file
        with open(file_path, 'r') as text_file:
            text = text_file.read()

        # Combine the prompt and the text
        payload = {"message": prompt + text, "mode": "chat"}
        logging.info(f"Payload: {payload}")

        # Send the POST request, ignoring SSL certificate errors
        response = requests.post(url, json=payload, headers=headers, verify=False)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Return the response text
        return response.json().get("textResponse", "")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Send a POST request with text and prompt.")
    parser.add_argument("-f", "--file", help="The path to the file containing the text.", required=False)
    parser.add_argument("-p", "--prompt", help="The path to the file containing the prompt.", required=False)
    parser.add_argument("-u", "--url", help="The URL to which the POST request will be sent.", required=False)
    parser.add_argument("-b", "--bearer", help="The Bearer token for authorization.", required=False)
    parser.add_argument("-c", "--config", help="The path to the configuration file.", required=False)
    parser.add_argument("-n", "--section", help="The section name in the configuration file.", required=False)

    # Parse the arguments
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_configuration(args)

        # Validate configuration
        validate_configuration(config)

        # Prepare headers
        headers = prepare_headers(config["bearer_token"])

        # Send POST request
        response_text = post_text_to_url(
            config["file_path"], config["prompt_path"], config["url"], headers
        )
        # Log and print the response
        logging.info(f"Response: {response_text}")
        print(response_text)
    except ValueError as e:
        logging.error(f"Configuration Error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error(f"File Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
