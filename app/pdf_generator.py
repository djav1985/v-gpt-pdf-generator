# pdf_generator.py
import pdfkit

def generate_pdf(html_content, css_content, output_path, options=None):
    default_options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
        'custom-header': [('Accept-Encoding', 'gzip')],
        'no-outline': None
    }
    if options:
        default_options.update(options)

    if css_content:
        html_content = f"<style>{css_content}</style>{html_content}"

    try:
        pdfkit.from_string(html_content, output_path, options=default_options)
    except Exception as e:
        raise Exception(f"Failed to generate PDF: {str(e)}")

# Test the function
if __name__ == "__main__":
    html_content = "<h1>Hello, World!</h1>"
    css_content = "h1 { color: red; }"
    output_path = "test.pdf"
    generate_pdf(html_content, css_content, output_path)
