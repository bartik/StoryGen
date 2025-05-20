import os
import glob
import re
import argparse
import configparser
import sys
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

    # Check if the split pattern exists in the "SPLIT PATTERN" section
    split_pattern = None
    if "SPLIT PATTERN" in config and args.split:
        split_pattern = config.get("SPLIT PATTERN", args.split, fallback=None)

    # Load and override configuration
    return {
        "source": args.source or config.get(section, "source", fallback=None),
        "destination": args.destination or config.get(section, "destination", fallback=None),
        "pattern": args.pattern or config.get(section, "pattern", fallback=None),
        "find": args.find or config.get(section, "find", fallback=None),
        "replace": args.replace or config.get(section, "replace", fallback=None),
        "split": split_pattern or args.split or config.get(section, "split", fallback=None),
    }

def validate_configuration(config):
    """
    Validate the configuration to ensure all required parameters are provided.

    Parameters:
        config (dict): Configuration dictionary.

    Raises:
        ValueError: If any required parameter is missing.
    """
    required_keys = ["source", "destination", "pattern", "find", "replace", "split"]
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        logging.error(f"Missing required parameters: {', '.join(missing_keys)}")
        raise ValueError(f"Missing required parameters: {', '.join(missing_keys)}")

def process_files(SRC_PATH, DST_PATH, PATTERN, FIND_STR, REPLACE_STR, SPLIT_STR):
    """
    Process all files in the SRC_PATH matching the supplied pattern.
    The content is split using the SPLIT_STR pattern.
    Each split unit is written to a separate file in DST_PATH with the naming convention:
    [REPLACE_STR]_[original_number]_[unit_number].txt.

    Parameters:
        SRC_PATH (str): The source directory containing the files to process.
        DST_PATH (str): The destination directory where the output files will be written.
        PATTERN (str): The pattern to match files in the SRC_PATH.
        FIND_STR (str): The string to find in the file name.
        REPLACE_STR (str): The string to replace the FIND_STR with in the file name.
        SPLIT_STR (str): The regex pattern used to split the content.
    """
    # Ensure the destination directory exists
    os.makedirs(DST_PATH, exist_ok=True)

    # Find all files matching the pattern
    pattern = os.path.join(SRC_PATH, PATTERN)
    for file_path in glob.glob(pattern):
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        
        # Replace FIND_STR with REPLACE_STR in the base name
        base_name = base_name.replace(FIND_STR, REPLACE_STR)
        
        # Read the file content
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError as e:
            logging.error(f"File not found: {file_path}. Error: {e}")
            continue

        # Split the content using the SPLIT_STR pattern
        units = [p.strip() for p in re.split(SPLIT_STR, content) if p.strip()]
        
        # Write each unit to a separate file
        for i, unit in enumerate(units, start=1):
            output_file_name = f"{base_name}_{i:02}.txt"
            output_file_path = os.path.join(DST_PATH, output_file_name)
            try:
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(unit)
                logging.info(f"Written: {output_file_path}")
            except Exception as e:
                logging.error(f"Error writing to file {output_file_path}: {e}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process text files by splitting their content.")
    parser.add_argument("-s", "--source", help="The source directory containing the files.", required=False)
    parser.add_argument("-d", "--destination", help="The destination directory for output files.", required=False)
    parser.add_argument("-p", "--pattern", help="The pattern to match files in the source directory.", required=False)
    parser.add_argument("-f", "--find", help="The string to find in the file name.", required=False)
    parser.add_argument("-r", "--replace", help="The string to replace the find string with in the file name.", required=False)
    parser.add_argument("-l", "--split", help="The regex pattern used to split the content.", required=False)
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
        process_files(
            config["source"],
            config["destination"],
            config["pattern"],
            config["find"],
            config["replace"],
            config["split"],
        )
    except ValueError as e:
        logging.error(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
