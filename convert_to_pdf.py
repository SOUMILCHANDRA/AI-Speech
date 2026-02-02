import markdown
from xhtml2pdf import pisa
import os

def convert_md_to_pdf(source_md, output_pdf):
    # Read Markdown
    with open(source_md, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert to HTML
    # Using 'extra' extension for tables, code blocks, etc.
    html_text = markdown.markdown(text, extensions=['extra', 'codehilite'])

    # Add some basic CSS for better pdf formatting
    css = """
    <style>
        body { font-family: Helvetica, sans-serif; font-size: 12px; line-height: 1.5; }
        h1 { color: #2c3e50; font-size: 24px; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
        h2 { color: #34495e; font-size: 18px; margin-top: 20px; }
        h3 { color: #7f8c8d; font-size: 14px; margin-top: 15px; }
        code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 4px; font-family: Consolas, monospace; }
        pre { background-color: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: Consolas, monospace; white-space: pre-wrap; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        blockquote { border-left: 4px solid #ddd; padding-left: 10px; color: #666; font-style: italic; }
    </style>
    """
    
    full_html = f"<html><head>{css}</head><body>{html_text}</body></html>"

    # Write PDF
    with open(output_pdf, "wb") as result_file:
        pisa_status = pisa.CreatePDF(
            full_html,
            dest=result_file
        )

    if pisa_status.err:
        print(f"Error converting to PDF: {pisa_status.err}")
    else:
        print(f"Successfully created PDF: {output_pdf}")

if __name__ == "__main__":
    # Source is the walkthrough artifact
    source = r"C:\Users\Admin\.gemini\antigravity\brain\010d81bb-c841-44ac-9138-e5e8357e3517\walkthrough.md"
    # Output to the project output directory
    output = r"d:\audiodetection\output\project_report.pdf"
    
    if os.path.exists(source):
        convert_md_to_pdf(source, output)
    else:
        print(f"Source file not found: {source}")
