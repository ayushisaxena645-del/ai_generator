import os
from jinja2 import Template


def load_file_content(file_path):
    """Utility helper to read text file contents."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Required template file '{file_path}' not found."
        )

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_portfolio_html(
    data,
    template_path="template.html",
    css_path="style.css",
    output_path="portfolio.html"
):
    """
    Renders structured resume dictionary into a standalone HTML page.
    """

    template_str = load_file_content(template_path)
    css_str = load_file_content(css_path)

    # Add CSS to the HTML
    render_context = dict(data)
    render_context["css_content"] = css_str

    template = Template(template_str)
    rendered_html = template.render(**render_context)

    # IMPORTANT:
    # Vercel has a read-only filesystem.
    # Do NOT save portfolio.html to disk.
    print("[SUCCESS] Portfolio webpage generated successfully.")

    return rendered_html
