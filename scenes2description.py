import os
import glob
import sys
import subprocess
import argparse
import configparser
import logging

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
        "source": args.source or config.get(section, "source", fallback=None),
        "destination": args.destination or config.get(section, "destination", fallback=None),
        "pattern": args.pattern or config.get(section, "pattern", fallback=None),
        "find": args.find or config.get(section, "find", fallback=None),
        "replace": args.replace or config.get(section, "replace", fallback=None),
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
    required_keys = ["source", "destination", "pattern", "find", "replace"]
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        logging.error(f"Missing required parameters: {', '.join(missing_keys)}")
        raise ValueError(f"Missing required parameters: {', '.join(missing_keys)}")

def process_files(config, args):
    """
    Process files based on the configuration.

    Parameters:
        config (dict): Configuration dictionary.
        args (Namespace): Parsed command-line arguments.
    """
    # Define the prompt file
    prompt_file = os.path.join(config["source"], f"{config['replace']}prompt.txt")

    # Ensure the destination directory exists
    os.makedirs(config["destination"], exist_ok=True)

    # Iterate over all files matching the pattern in the source directory
    pattern = os.path.join(config["source"], config["pattern"])
    for file_path in glob.glob(pattern):
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        logging.info(f"Processing file: {file_name}")

        # Replace FIND_STR with REPLACE_STR in the output file name
        output_file_name = file_name.replace(config["find"], config["replace"])
        output_file = os.path.join(config["destination"], f"{output_file_name}.txt")

        # Construct the command to be invoked
        command = [
            "python",
            "ewardea.py",
            "-f", file_path,  # Add the -f switch for file_path
            "-p", prompt_file  # Add the -p switch for prompt_file
        ]

        # Include optional parameters in the command
        if args.url:
            command.extend(["-u", args.url])
        if args.bearer:
            command.extend(["-b", args.bearer])
        if args.config:
            command.extend(["-c", args.config])
        if args.section:
            command.extend(["-n", args.section])

        logging.info(f"Command to execute: {command}")
        # Execute the command and redirect output to the output file
        try:
            with open(output_file, "w", encoding="utf-8") as output:
                subprocess.run(command, stdout=output, stderr=subprocess.PIPE, check=True)
            logging.info(f"Output written to: {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error processing {file_path}: {e.stderr.decode().strip()}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process scene files and generate descriptions.")
    parser.add_argument("-s", "--source", help="The source directory containing the files.", required=False)
    parser.add_argument("-d", "--destination", help="The destination directory for output files.", required=False)
    parser.add_argument("-p", "--pattern", help="The pattern to match files in the source directory.", required=False)
    parser.add_argument("-f", "--find", help="The string to find in the file name.", required=False)
    parser.add_argument("-r", "--replace", help="The string to replace the find string with in the file name.", required=False)
    parser.add_argument("-b", "--bearer", help="The Bearer token for authorization.", required=False)
    parser.add_argument("-u", "--url", help="The URL to which the POST request will be sent.", required=False)
    parser.add_argument("-c", "--config", help="The path to the configuration file.", required=False)
    parser.add_argument("-n", "--section", help="The section name in the configuration file.", required=False)

    # Parse the arguments
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_configuration(args)

        # Validate configuration
        validate_configuration(config)

        # Process files
        process_files(config, args)
    except ValueError as e:
        logging.error(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
