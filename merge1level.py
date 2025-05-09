import os
import glob
import sys

def merge_files(SRC_PATH, DST_PATH, PATTERN, FIND_STR, REPLACE_STR):
    """
    Reads files from SRC_PATH matching the PATTERN and writes their content into a file in DST_PATH
    where the last part of the source file name (separated by underscores) is removed.

    Parameters:
        SRC_PATH (str): The source directory containing the files to process.
        DST_PATH (str): The destination directory where the merged files will be written.
        PATTERN (str): The pattern to match files in the SRC_PATH.
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
        with open(file_path, 'r', encoding='utf-8') as src_file:
            content = src_file.read()
        
        # Write the content to the destination file
        with open(output_file_path, 'a', encoding='utf-8') as dst_file:
            dst_file.write(content + "\n\n")
        
        print(f"Merged: {file_path} -> {output_file_path}")

# Example usage
if __name__ == "__main__":
    # Check if the required arguments are provided
    if len(sys.argv) < 6:
        print("Usage: python merge1level.py <SRC_PATH> <DST_PATH> <PATTERN> <FIND_STR> <REPLACE_STR>")
        sys.exit(1)

    # Read SRC_PATH, DST_PATH, and PATTERN from command-line arguments
    SRC_PATH = sys.argv[1]
    DST_PATH = sys.argv[2]
    PATTERN = sys.argv[3]
    FIND_STR = sys.argv[4]
    REPLACE_STR = sys.argv[5]

    # Merge files
    merge_files(SRC_PATH, DST_PATH, PATTERN, FIND_STR, REPLACE_STR)
