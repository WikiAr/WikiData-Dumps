def is_docstring(line: str) -> bool:
    """
    Check if a given line is a docstring.

    Args:
        line: The line of code to check.

    Returns:
        True if the line is a docstring, False otherwise.
    """
    return line.strip().startswith('"""') or line.strip().startswith("'''")

def is_comment(line: str) -> bool:
    """
    Check if a given line is a comment.

    Args:
        line: The line of code to check.

    Returns:
        True if the line is a comment, False otherwise.
    """
    return line.strip().startswith('#')

def update_docstrings_and_comments(file_path: str) -> None:
    """
    Update the docstrings and comments in the specified file.

    Args:
        file_path: The path to the file to update.
    """
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if is_docstring(line) or is_comment(line):
                file.write(line)
            else:
                file.write('\n')
        file.truncate()

def main():
    file_path = 'labels/old/labels2.py'
    update_docstrings_and_comments(file_path)

if __name__ == '__main__':
    main()
