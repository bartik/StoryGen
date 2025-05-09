import os
import glob
import sys
import subprocess

# Check if the required arguments are provided
if len(sys.argv) < 6:
    print("Usage: python scenes2description.py <SRC_PATH> <DST_PATH> <PATTERN> <FIND_STR> <REPLACE_STR>")
    sys.exit(1)

# Define source and destination paths
SRC_PATH = sys.argv[1]
DST_PATH = sys.argv[2]
PATTERN = sys.argv[3]
FIND_STR = sys.argv[4]
REPLACE_STR = sys.argv[5]
PROMPT_FILE = os.path.join(SRC_PATH, f"{REPLACE_STR}prompt.txt")

# Ensure the destination directory exists
os.makedirs(DST_PATH, exist_ok=True)

# Iterate over all files matching the pattern in the SRC_PATH
pattern = os.path.join(SRC_PATH, PATTERN)

# Find all files matching the pattern
for file_path in glob.glob(pattern):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"Processing file: {file_name}")
    
    # Replace FIND_STR with REPLACE_STR in the output file name
    output_file_name = file_name.replace(FIND_STR, REPLACE_STR)
    output_file = os.path.join(DST_PATH, f"{output_file_name}.txt")
    
    # Construct the command to be invoked
    command = [
        "python",
        "ewardea.py",
        file_path,
        PROMPT_FILE
    ]
    
    # Execute the command and redirect output to the output file
    try:
        with open(output_file, "w", encoding="utf-8") as output:
            subprocess.run(command, stdout=output, stderr=subprocess.PIPE, check=True)
        print(f"Output written to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {file_path}: {e.stderr.decode().strip()}")
