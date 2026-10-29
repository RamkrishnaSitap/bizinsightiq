"""
Convert docs/BIZINSIGHTIQ_COMPLETE_BEGINNER_LEARNING_GUIDE.md into a beautifully styled HTML file
ready for A4 PDF compilation.
"""
import os
import re
import html

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
MD_FILE = os.path.join(DOCS_DIR, "BIZINSIGHTIQ_COMPLETE_BEGINNER_LEARNING_GUIDE.md")
HTML_FILE = os.path.join(DOCS_DIR, "BIZINSIGHTIQ_COMPLETE_BEGINNER_LEARNING_GUIDE.html")


def parse_markdown_to_html(md_text):
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    code_block_lang = ""
    code_lines = []
    in_table = False
    table_rows = []
    in_list = False
    list_type = None

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            html_lines.append(f"</{list_type}>")
            in_list = False
            list_type = None

    def close_table():
        nonlocal in_table, table_rows
        if in_table and table_rows:
            html_lines.append('<div class="table-container">')
            html_lines.append('<table class="guide-table">')
            headers = table_rows[0]
            html_lines.append("<thead><tr>")
            for h in headers:
                html_lines.append(f"<th>{inline_format(h)}</th>")
            html_lines.append("</tr></thead>")
            html_lines.append("<tbody>")
            for r in table_rows[1:]:
                html_lines.append("<tr>")
                for cell in r:
                    html_lines.append(f"<td>{inline_format(cell)}</td>")
                html_lines.append("</tr>")
            html_lines.append("</tbody>")
            html_lines.append("</table>")
            html_lines.append("</div>")
            in_table = False
            table_rows = []

    def inline_format(text):
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        text = re.sub(r'\$\$(.*?)\$\$', r'<span class="math-display">\1</span>', text)
        text = re.sub(r'\$(.*?)\$', r'<span class="math-inline">\1</span>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle Code blocks
        if stripped.startswith("```"):
            close_list()
            close_table()
            if not in_code_block:
                in_code_block = True
                code_block_lang = stripped[3:].strip()
                code_lines = []
            else:
                in_code_block = False
                code_content = html.escape("\n".join(code_lines))
                html_lines.append(f'<pre><code class="lang-{code_block_lang}">{code_content}</code></pre>')
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Handle Table rows
        if stripped.startswith("|") and stripped.endswith("|"):
            close_list()
            parts = [p.strip() for p in stripped.split("|")[1:-1]]
            if all(re.match(r'^:?-+:?$', p) for p in parts if p):
                pass
            else:
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(parts)
            i += 1
            continue
        else:
            close_table()

        # Empty lines
        if not stripped:
            close_list()
            close_table()
            i += 1
            continue

        # Horizontal Rule
        if stripped in ["---", "***", "___"]:
            close_list()
            close_table()
            html_lines.append('<hr class="section-divider" />')
            i += 1
            continue

        # Headings
        if stripped.startswith("#"):
            close_list()
            close_table()
            level = len(stripped.split()[0])
            title = stripped[level:].strip()
            extra_class = ""
            if level == 1 and ("PART " in title.upper() or "SECTION " in title.upper()):
                extra_class = " part-heading"
            elif level == 2 and "CHAPTER " in title.upper():
                extra_class = " chapter-heading"
            elif level == 2 and "DOCUMENT NAVIGATION" in title.upper():
                extra_class = " toc-heading"
            html_lines.append(f'<h{level} class="heading-{level}{extra_class}">{inline_format(title)}</h{level}>')
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            close_list()
            close_table()
            quote_text = stripped[1:].strip()
            html_lines.append(f'<blockquote>{inline_format(quote_text)}</blockquote>')
            i += 1
            continue

        # Unordered List
        if re.match(r'^[-*+]\s+', stripped):
            close_table()
            item_text = re.sub(r'^[-*+]\s+', '', stripped)
            # Check for checklist
            if item_text.startswith("[ ] "):
                item_text = '<input type="checkbox" disabled /> ' + item_text[4:]
            elif item_text.startswith("[x] "):
                item_text = '<input type="checkbox" checked disabled /> ' + item_text[4:]

            if not in_list or list_type != "ul":
                close_list()
                in_list = True
                list_type = "ul"
                html_lines.append('<ul class="guide-list">')
            html_lines.append(f'<li>{inline_format(item_text)}</li>')
            i += 1
            continue

        # Ordered List
        ordered_match = re.match(r'^(\d+)\.\s+', stripped)
        if ordered_match:
            close_table()
            item_text = stripped[len(ordered_match.group(0)):]
            if not in_list or list_type != "ol":
                close_list()
                in_list = True
                list_type = "ol"
                html_lines.append('<ol class="guide-list">')
            html_lines.append(f'<li>{inline_format(item_text)}</li>')
            i += 1
            continue

        # Paragraph
        close_list()
        close_table()
        html_lines.append(f'<p class="guide-para">{inline_format(stripped)}</p>')
        i += 1

    close_list()
    close_table()
    return "\n".join(html_lines)


def build_full_html():
    print(f"Reading markdown from: {MD_FILE}")
    with open(MD_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()

    body_html = parse_markdown_to_html(md_text)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BizInsightIQ: Complete Project Learning Guide for an Absolute Beginner</title>
  <style>
    @page {{
      size: A4;
      margin: 20mm 20mm 25mm 25mm;
      @bottom-right {{
        content: counter(page);
      }}
    }}

    body {{
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.55;
      color: #1a202c;
      background: #fff;
      margin: 0;
      padding: 0;
    }}

    .section-divider {{
      border: none;
      border-top: 1px solid #cbd5e0;
      margin: 20px 0;
    }}

    h1.part-heading {{
      page-break-before: always;
      page-break-after: avoid;
      break-after: avoid;
      color: #1a365d;
      background: #edf2f7;
      border-left: 6px solid #2b6cb0;
      border-bottom: 2px solid #2b6cb0;
      padding: 12px 18px;
      margin-top: 24px;
      margin-bottom: 16px;
      font-size: 15pt;
      letter-spacing: 0.5px;
    }}

    h2.chapter-heading {{
      page-break-before: auto;
      page-break-after: avoid;
      break-after: avoid;
      color: #2b6cb0;
      border-bottom: 1.5px solid #cbd5e0;
      padding-bottom: 4px;
      margin-top: 22px;
      margin-bottom: 10px;
      font-size: 13pt;
    }}

    h2.toc-heading {{
      color: #2d3748;
      border-bottom: 2px solid #2b6cb0;
      padding-bottom: 4px;
      margin-top: 20px;
      margin-bottom: 12px;
    }}

    h1, h2, h3, h4, h5, h6 {{
      page-break-after: avoid;
      break-after: avoid;
    }}

    h1 {{
      font-size: 18pt;
      color: #2b6cb0;
      text-align: center;
      margin-bottom: 8px;
    }}

    h2 {{
      font-size: 14pt;
      color: #2d3748;
      margin-top: 24px;
      margin-bottom: 10px;
    }}

    h3 {{
      font-size: 12pt;
      color: #4a5568;
      margin-top: 18px;
      margin-bottom: 8px;
    }}

    h4 {{
      font-size: 11pt;
      color: #718096;
      margin-top: 14px;
      margin-bottom: 6px;
    }}

    p.guide-para {{
      margin: 0 0 10px 0;
      text-align: justify;
    }}

    blockquote {{
      margin: 14px 0;
      padding: 10px 18px;
      background: #ebf8ff;
      border-left: 4px solid #3182ce;
      color: #2c5282;
      border-radius: 4px;
    }}

    code {{
      font-family: 'Consolas', 'Courier New', Courier, monospace;
      font-size: 9.5pt;
      background: #edf2f7;
      padding: 2px 5px;
      border-radius: 3px;
      color: #805ad5;
    }}

    pre {{
      background: #1a202c;
      color: #f7fafc;
      padding: 14px 16px;
      border-radius: 6px;
      overflow-x: auto;
      font-family: 'Consolas', 'Courier New', Courier, monospace;
      font-size: 9pt;
      line-height: 1.45;
      margin: 14px 0;
      page-break-inside: avoid;
    }}

    pre code {{
      background: transparent;
      padding: 0;
      color: inherit;
    }}

    .table-container {{
      width: 100%;
      margin: 16px 0;
      overflow-x: auto;
      page-break-inside: avoid;
    }}

    table.guide-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 9.5pt;
    }}

    table.guide-table th, table.guide-table td {{
      border: 1px solid #cbd5e0;
      padding: 6px 10px;
      text-align: left;
      vertical-align: top;
    }}

    table.guide-table th {{
      background-color: #edf2f7;
      font-weight: 600;
      color: #2d3748;
    }}

    table.guide-table tr:nth-child(even) {{
      background-color: #f7fafc;
    }}

    ul.guide-list, ol.guide-list {{
      margin: 6px 0 12px 0;
      padding-left: 24px;
    }}

    li {{
      margin-bottom: 4px;
    }}

    a {{
      color: #3182ce;
      text-decoration: none;
    }}

    .math-inline {{
      font-family: 'Cambria Math', 'Times New Roman', serif;
      font-style: italic;
    }}

    .math-display {{
      display: block;
      text-align: center;
      margin: 10px 0;
      font-family: 'Cambria Math', 'Times New Roman', serif;
      font-style: italic;
    }}
  </style>
</head>
<body>
  {body_html}
</body>
</html>
"""

    print(f"Writing compiled HTML to: {HTML_FILE}")
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(full_html)
    print("HTML build complete!")


if __name__ == "__main__":
    build_full_html()
