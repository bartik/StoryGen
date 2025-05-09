import os
import glob
import re
import sys

def process_files(SRC_PATH, DST_PATH, PATTERN, FIND_STR, REPLACE_STR):
    """
    Process all files in SRC_PATH matching the supplied pattern.
    Each sentence from the file is written to a separate file in DST_PATH with the naming convention:
    sentence_[original_numbers]_[sentence_number].txt.

    Parameters:
        SRC_PATH (str): The source directory containing the files to process.
        DST_PATH (str): The destination directory where the output files will be written.
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
        
        # Replace FIND_STR with REPLACE_STR in the base name
        base_name = base_name.replace(FIND_STR, REPLACE_STR)
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split the content into sentences using a regex
        sentences = re.split(r'(?<=[.!?])\s+', content.strip())
        
        # Write each sentence to a separate file
        for i, sentence in enumerate(sentences, start=1):
            output_file_name = f"{base_name}_{i:04}.txt"
            output_file_path = os.path.join(DST_PATH, output_file_name)
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(sentence)

# Example usage
if __name__ == "__main__":
    # Check if the required arguments are provided
    if len(sys.argv) < 6:
        print("Usage: python paragraph2sentences.py <SRC_PATH> <DST_PATH> <PATTERN> <FIND_STR> <REPLACE_STR>")
        sys.exit(1)

    # Read SRC_PATH, DST_PATH, and PATTERN from command-line arguments
    SRC_PATH = sys.argv[1]
    DST_PATH = sys.argv[2]
    PATTERN = sys.argv[3]
    FIND_STR = sys.argv[4]
    REPLACE_STR = sys.argv[5]

    # Process the files
    process_files(SRC_PATH, DST_PATH, PATTERN, FIND_STR, REPLACE_STR)
