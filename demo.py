# Define the function to generate the HTML code

def generate_html(title, body):
    """
    Generate an HTML document with a given title and body.

    Args:
    title (str): The title of the HTML document.
    body (str): The body content of the HTML document.

    Returns:
    str: The generated HTML document as a string.
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
    </head>
    <body>
        {body}
    </body>
    </html>
    """
    return html_template.format(title=title, body=body)

# Example usage

title = "My HTML Document"
body = "<h1>This is a sample HTML document.</h1>"

html_doc = generate_html(title, body)
print(html_doc)