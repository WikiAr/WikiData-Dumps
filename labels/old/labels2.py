import os

def remove_trailing_whitespace(file_path):
    # Read the contents of the file
    content = read_file(file_path)

    # Split the content into lines
    lines = content.split('\n')

    # Remove trailing whitespace from each line
    cleaned_lines = [line.rstrip() for line in lines]

    # Join the cleaned lines back into a single string
    cleaned_content = '\n'.join(cleaned_lines)

    # Write the cleaned content back to the file
    write_file(file_path, cleaned_content)

# Read the contents of a file and return it as a string
def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

# Write the given content to a file
def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

# Remove trailing whitespace from the file "labels/old/labels2.py"
remove_trailing_whitespace("labels/old/labels2.py")
