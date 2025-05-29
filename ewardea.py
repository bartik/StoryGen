import sys
import requests
import urllib3
import argparse
import configparser
import logging
import json

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
        list: tag_file_tuples, a list of (tag, file_name) tuples from config or CLI.
    """
    config = configparser.ConfigParser()
    tag_file_tuples = []
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

    # Read tag_file_tuples only from keys named 'tag_file' that contain a comma
    if section in config:
        for key, value in config.items(section):
            if key == "tag_file":
                for line in value.splitlines():
                    line = line.strip()
                    if ',' in line:
                        tag, file_name = line.split(',', 1)
                        tag_file_tuples.append((tag.strip(), file_name.strip()))

    # Add/override with positional arguments from CLI
    for tf in args.tag_file:
        if ',' not in tf:
            logging.error(f"Invalid positional argument format: '{tf}'. Expected <tag>,<file_name>.")
            sys.exit(1)
        tag, file_name = tf.split(',', 1)
        tag_file_tuples.append((tag.strip(), file_name.strip()))

    # Load and override configuration
    return {
        "prompt_path": args.prompt or config.get(section, "prompt", fallback=None),
        "url": args.url or config.get(section, "url", fallback=None),
        "bearer_token": args.bearer or config.get(section, "bearer", fallback=None),
    }, tag_file_tuples

def validate_configuration(config, tag_file_tuples):
    """
    Validate the configuration to ensure all required parameters are provided.

    Parameters:
        config (dict): Configuration dictionary.
        tag_file_tuples (list): List of (tag, file_name) tuples.

    Raises:
        ValueError: If any required parameter is missing.
    """
    required_keys = ["prompt_path", "url", "bearer_token"]
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        logging.error(f"Missing required parameters: {', '.join(missing_keys)}")
        raise ValueError(f"Missing required parameters: {', '.join(missing_keys)}")
    if not tag_file_tuples:
        logging.error("No tag_file_tuples provided (either in config or as positional arguments).")
        raise ValueError("No tag_file_tuples provided (either in config or as positional arguments).")

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

def build_payload_str(prompt, tag_file_tuples):
    """
    Build the payload string by appending text from tag/file tuples to the prompt.

    Parameters:
        prompt (str): The prompt text.
        tag_file_tuples (list): List of (tag, file_name) tuples.

    Returns:
        str: The constructed payload string.
    """
    payload_str = prompt
    for tag, file_name in tag_file_tuples:
        try:
            with open(file_name, 'r', errors='ignore') as text_file:
                text = text_file.read()
        except FileNotFoundError:
            logging.error(f"File not found (skipped): {file_name}")
            continue  # Skip this file and continue with the next
        except Exception as e:
            logging.error(f"Error reading file '{file_name}' (skipped): {e}")
            continue  # Skip this file and continue with the next
        if tag == "SQUAREBRACKETS":
            payload_str += f"\n[{text}]\n"
        elif tag == "CURLYBRACKETS":
            payload_str += f"\n{{{text}}}\n"
        elif tag == "PARENTHESES":
            payload_str += f"\n({text})\n"
        elif tag == "ANGLEBRACKETS":
            payload_str += f"\n<{text}>\n"
        else:
            payload_str += f"\n{tag}\n{text}\n{tag}\n"
    return payload_str

def post_text_to_url(prompt_path, url, headers, tag_file_tuples):
    """
    Reads a prompt from a file, appends text from tag/file tuples, and sends it as a POST request.

    Parameters:
        prompt_path (str): The path to the file containing the prompt.
        url (str): The URL to which the POST request will be sent.
        headers (dict): Headers for the POST request.
        tag_file_tuples (list): List of (tag, file_name) tuples.

    Returns:
        str: The response text from the server.
    """
    try:
        # Read the prompt from the prompt file
        with open(prompt_path, 'r', errors='ignore') as prompt_file:
            prompt = prompt_file.read()

        # Build the payload string using the new function
        payload_str = build_payload_str(prompt, tag_file_tuples)
        payload_str = json.dumps(payload_str)
        payload = {"message": payload_str, "mode": "chat"}
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

def run(args):
    # Load configuration and tag_file_tuples
    try:
        config, tag_file_tuples = load_configuration(args)

        # Validate configuration
        validate_configuration(config, tag_file_tuples)

        # Prepare headers
        headers = prepare_headers(config["bearer_token"])

        # Send POST request
        response_text = post_text_to_url(
            config["prompt_path"], config["url"], headers, tag_file_tuples
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

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Send a POST request with text and prompt.")
    parser.add_argument("-p", "--prompt", help="The path to the file containing the prompt.", required=False)
    parser.add_argument("-u", "--url", help="The URL to which the POST request will be sent.", required=False)
    parser.add_argument("-b", "--bearer", help="The Bearer token for authorization.", required=False)
    parser.add_argument("-c", "--config", help="The path to the configuration file.", required=False)
    parser.add_argument("-n", "--section", help="The section name in the configuration file.", required=False)
    parser.add_argument("tag_file", nargs="*", help="Tuples in the format <tag>,<file_name>")

    # Parse the arguments
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()
