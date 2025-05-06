import os

# Define a map for comment styles based on file extensions
COMMENT_STYLES = {
    '.py': '#',  # Python
    '.js': '//',  # JavaScript
    '.java': '//',  # Java
    '.html': '<!-- -->',  # HTML
    '.css': '/* */',  # CSS
}

def get_comment_style(file_path):
    """
    Determine the comment style based on the file extension.
    """
    _, ext = os.path.splitext(file_path)
    return COMMENT_STYLES.get(ext, None)

def add_comment(file_path, comment_text):
    """
    Add a comment to the top of a file with the appropriate comment style.
    """
    comment_style = get_comment_style(file_path)
    if not comment_style:
        print(f"Unsupported file type for: {file_path}")
        return

    # Read the existing content
    with open(file_path, 'r') as file:
        content = file.readlines()

    # Prepare the comment based on the style
    if comment_style in ['#', '//']:
        comment = f"{comment_style} {comment_text}\n"
    elif comment_style == '<!-- -->':
        comment = f"<!-- {comment_text} -->\n"
    elif comment_style == '/* */':
        comment = f"/* {comment_text} */\n"
    else:
        print(f"Unsupported comment style: {comment_style}")
        return

    # Write the comment at the top and add the existing content
    with open(file_path, 'w') as file:
        file.write(comment)
        file.writelines(content)

# Example usage
add_comment('example.py', 'This is a Python file')
add_comment('example.js', 'This is a JavaScript file')
