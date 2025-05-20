import os
import glob
import sys
import argparse
import configparser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def merge_files(SRC_PATH, DST_PATH, PATTERN, FIND_STR, REPLACE_STR):
    """
    Reads files from SRC_PATH matching the PATTERN and writes their content into a file in DST_PATH
    where the last part of the source file name (separated by underscores) is removed.

    Parameters:
        SRC_PATH (str): The source directory containing the files to process.
        DST_PATH (str): The destination directory where the merged files will be written.
        PATTERN (str): The pattern to match files in the SRC_PATH.
        FIND_STR (str): The string to find in the file name.
        REPLACE_STR (str): The string to replace the FIND_STR with in the file name.
    """
    # Ensure the destination directory exists
    os.makedirs(DST_PATH, exist_ok=True)

    # Find all files matching the pattern
    pattern = os.path.join(SRC_PATH, PATTERN)
    for file_path in glob.glob(pattern):
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        
        # Remove the last part of the file name (separated by underscores)
        new_base_name = "_".join(base_name.split("_")[:-1])

        # Replace FIND_STR with REPLACE_STR in the base name
        new_base_name = new_base_name.replace(FIND_STR, REPLACE_STR)

        output_file_name = f"{new_base_name}.txt"
        output_file_path = os.path.join(DST_PATH, output_file_name)
        
        # Read the content of the source file
        try:
            with open(file_path, 'r', encoding='utf-8') as src_file:
                content = src_file.read()
        except FileNotFoundError as e:
            logging.error(f"File not found: {file_path}. Error: {e}")
            continue
        
        # Write the content to the destination file
        try:
            with open(output_file_path, 'a', encoding='utf-8') as dst_file:
                dst_file.write(content + "\n\n")
            logging.info(f"Merged: {file_path} -> {output_file_path}")
        except Exception as e:
            logging.error(f"Error writing to file {output_file_path}: {e}")

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
            if not config.sections():
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
    }

def validate_configuration(config):
    """
    Validate the configuration to ensure all required parameters are provided.

    Parameters:
        config (dict): Configuration dictionary.

    Raises:
        ValueError: If any required parameter is missing.
    """
    required_keys = ["source", "destination", "pattern"]
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        logging.error(f"Missing required parameters: {', '.join(missing_keys)}")
        raise ValueError(f"Missing required parameters: {', '.join(missing_keys)}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Merge text files by removing the last part of their names.")
    parser.add_argument("-s", "--source", help="The source directory containing the files.", required=False)
    parser.add_argument("-d", "--destination", help="The destination directory for output files.", required=False)
    parser.add_argument("-p", "--pattern", help="The pattern to match files in the source directory.", required=False)
    parser.add_argument("-f", "--find", help="The string to find in the file name.", required=False)
    parser.add_argument("-r", "--replace", help="The string to replace the find string with in the file name.", required=False)
    parser.add_argument("-c", "--config", help="The path to the configuration file.", required=False)
    parser.add_argument("-n", "--section", help="The section name in the configuration file.", required=False)

    # Parse the arguments
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_configuration(args)

        # Validate configuration
        validate_configuration(config)

        # Merge files
        merge_files(
            config["source"],
            config["destination"],
            config["pattern"],
            config["find"] or "",
            config["replace"] or "",
        )
    except ValueError as e:
        logging.error(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
