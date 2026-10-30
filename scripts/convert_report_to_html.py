"""
Convert docs/mca_project_report.md into a beautifully styled HTML file
ready for A4 academic PDF compilation according to LPU CDOE guidelines.
"""
import os
import re
import base64
import html

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
MD_FILE = os.path.join(DOCS_DIR, "mca_project_report.md")
HTML_FILE = os.path.join(DOCS_DIR, "mca_project_report.html")


def image_to_base64(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{base64.b64encode(data).decode('utf-8')}"


def parse_markdown_to_html(md_text):
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    code_block_lang = ""
    code_lines = []
    in_table = False
    table_rows = []
    in_list = False
    list_type = None  # 'ul' or 'ol'

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
            html_lines.append('<table class="academic-table">')
            # First row is header
            headers = table_rows[0]
            html_lines.append("<thead><tr>")
            for h in headers:
                html_lines.append(f"<th>{inline_format(h)}</th>")
            html_lines.append("</tr></thead>")
            # Remaining rows are body (skipping row 1 if it's separator)
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
        # Escape HTML basic chars except if already html
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Inline images: ![alt](url)
        def replace_img(match):
            alt, src = match.group(1), match.group(2)
            # Check local file
            if src.startswith("screenshots/") or src.startswith("screenshots\\"):
                local_path = os.path.join(DOCS_DIR, src)
                if os.path.exists(local_path):
                    b64 = image_to_base64(local_path)
                    return f'<div class="figure-wrapper"><img src="{b64}" alt="{alt}" class="report-image" /><div class="figure-caption">{alt}</div></div>'
            elif "http" in src:
                return f'<div class="figure-wrapper"><img src="{src}" alt="{alt}" class="report-image" /><div class="figure-caption">{alt}</div></div>'
            return f'<img src="{src}" alt="{alt}" />'
            
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img, text)

        # Bold + Italic: ***text*** or ___text___
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        # Bold: **text**
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # Italic: *text*
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        # Inline Code: `code`
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        # LaTeX math: $$math$$ and $math$
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

        # Handle Table rows: starts and ends with |
        if stripped.startswith("|") and stripped.endswith("|"):
            close_list()
            parts = [p.strip() for p in stripped.split("|")[1:-1]]
            # Check if this is separator line like | :--- | :--- |
            if all(re.match(r'^:?-+:?$', p) for p in parts if p):
                # skip separator line
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
            html_lines.append('<hr class="page-break" />')
            i += 1
            continue

        # Headings
        if stripped.startswith("#"):
            close_list()
            close_table()
            level = len(stripped.split()[0])
            title = stripped[level:].strip()
            # Check if this heading indicates a new chapter
            extra_class = ""
            if "CHAPTER " in title.upper() or "ANNEXURE" in title.upper() or title.upper() in ["TABLE OF CONTENTS", "ABSTRACT", "ACKNOWLEDGEMENT", "REFERENCES"]:
                extra_class = " chapter-start"
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

        # Ordered List: 1. Item
        match_ol = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if match_ol:
            close_table()
            if not in_list or list_type != 'ol':
                close_list()
                in_list = True
                list_type = 'ol'
                html_lines.append('<ol class="report-list">')
            html_lines.append(f'<li>{inline_format(match_ol.group(2))}</li>')
            i += 1
            continue

        # Unordered List: - Item or * Item
        match_ul = re.match(r'^[-*]\s+(.*)$', stripped)
        if match_ul:
            close_table()
            if not in_list or list_type != 'ul':
                close_list()
                in_list = True
                list_type = 'ul'
                html_lines.append('<ul class="report-list">')
            html_lines.append(f'<li>{inline_format(match_ul.group(1))}</li>')
            i += 1
            continue

        # Normal Paragraph
        close_list()
        close_table()
        # Handle custom divs like <div align="center">
        if stripped.startswith("<div") or stripped.startswith("</div") or stripped.startswith("<img") or stripped.startswith("<br"):
            html_lines.append(stripped)
        else:
            html_lines.append(f'<p class="report-para">{inline_format(stripped)}</p>')
        i += 1

    close_list()
    close_table()
    return "\n".join(html_lines)


def build_full_html(body_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BizInsightIQ - MCA Capstone Project Report</title>
  <style>
    @page {{
      size: A4 portrait;
      margin: 25mm 20mm 20mm 25mm;
    }}
    
    body {{
      font-family: 'Times New Roman', Times, serif;
      font-size: 12pt;
      line-height: 1.5;
      color: #111;
      background-color: #fff;
      margin: 0;
      padding: 0;
      text-align: justify;
    }}

    .chapter-start {{
      page-break-before: always;
      margin-top: 30px;
      padding-top: 20px;
    }}

    .page-break {{
      page-break-before: always;
      border: none;
      margin: 0;
      padding: 0;
      visibility: hidden;
      height: 0;
    }}

    h1, h2, h3, h4, h5, h6 {{
      font-family: 'Times New Roman', Times, serif;
      color: #000;
      font-weight: bold;
      page-break-after: avoid;
    }}

    h1 {{
      font-size: 16pt;
      text-align: center;
      margin-top: 20px;
      margin-bottom: 16px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    h2 {{
      font-size: 14pt;
      margin-top: 24px;
      margin-bottom: 12px;
      border-bottom: 1px solid #ccc;
      padding-bottom: 4px;
    }}

    h3 {{
      font-size: 13pt;
      margin-top: 18px;
      margin-bottom: 8px;
    }}

    h4 {{
      font-size: 12pt;
      font-style: italic;
      margin-top: 14px;
      margin-bottom: 6px;
    }}

    p.report-para {{
      margin-top: 0;
      margin-bottom: 10px;
      text-indent: 20px;
    }}

    /* Table of contents & Front matter paras should not have indent */
    div[align="center"] p, blockquote p, td p, th p {{
      text-indent: 0 !important;
    }}

    blockquote {{
      margin: 15px 30px;
      padding: 10px 15px;
      background: #f8f9fa;
      border-left: 4px solid #2b5797;
      font-style: italic;
      page-break-inside: avoid;
    }}

    .table-container {{
      width: 100%;
      margin: 16px 0;
      page-break-inside: avoid;
    }}

    table.academic-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 10.5pt;
      margin: 0 auto;
      page-break-inside: avoid;
    }}

    table.academic-table th, table.academic-table td {{
      border: 1px solid #444;
      padding: 6px 8px;
      vertical-align: top;
      text-align: left;
    }}

    table.academic-table th {{
      background-color: #e9ecef;
      font-weight: bold;
      text-align: center;
    }}

    ul.report-list, ol.report-list {{
      margin-top: 4px;
      margin-bottom: 10px;
      padding-left: 28px;
    }}

    li {{
      margin-bottom: 4px;
    }}

    pre {{
      background-color: #f4f6f8;
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 10px 14px;
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 9.5pt;
      overflow-x: auto;
      page-break-inside: avoid;
      line-height: 1.35;
    }}

    code {{
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 10pt;
      background: #f0f2f5;
      padding: 1px 4px;
      border-radius: 3px;
    }}

    pre code {{
      background: none;
      padding: 0;
    }}

    .figure-wrapper {{
      text-align: center;
      margin: 18px 0;
      page-break-inside: avoid;
    }}

    img.report-image {{
      max-width: 92%;
      height: auto;
      border: 1px solid #ccc;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 6px;
    }}

    .figure-caption {{
      font-size: 10pt;
      font-weight: bold;
      color: #333;
      margin-top: 4px;
    }}

    .math-inline {{
      font-family: 'Cambria Math', 'Times New Roman', serif;
      font-style: italic;
    }}

    .math-display {{
      display: block;
      text-align: center;
      margin: 12px 0;
      font-family: 'Cambria Math', 'Times New Roman', serif;
      font-size: 11pt;
    }}

    /* Title page center alignment */
    div[align="center"] {{
      text-align: center;
    }}
  </style>
</head>
<body>
{body_html}
</body>
</html>
"""


def export_pdf_cdp():
    import subprocess
    import json
    import time
    import urllib.request
    import asyncio
    import websockets

    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_exe):
        print("Microsoft Edge not found at default path, skipping PDF export.")
        return

    port = 9222
    user_data_dir = os.path.abspath(r"C:\Users\Lenovo\.gemini\antigravity\brain\f7d14055-63ae-433e-9a8a-f4528e783b4a\scratch\edge_profile")
    html_uri = f"file:///{HTML_FILE.replace(os.sep, '/')}"
    out_pdf = os.path.join(DOCS_DIR, "mca_project_report_final.pdf")
    default_pdf = os.path.join(DOCS_DIR, "mca_project_report.pdf")

    cmd = [
        edge_exe,
        "--headless=new",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={user_data_dir}",
        "--disable-gpu",
        "--no-sandbox",
        "about:blank"
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2)

    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json")
        targets = json.loads(req.read().decode("utf-8"))
        page_targets = [t for t in targets if t.get("type") == "page"]
        ws_url = page_targets[0]["webSocketDebuggerUrl"]

        async def run_print():
            async with websockets.connect(ws_url, max_size=100*1024*1024) as ws:
                mid = 2001
                async def send(method, params=None):
                    nonlocal mid
                    await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
                    while True:
                        resp = json.loads(await ws.recv())
                        if resp.get("id") == mid:
                            mid += 1
                            return resp

                await send("Page.enable")
                await send("Page.navigate", {"url": html_uri})
                await asyncio.sleep(5)

                res = await send("Page.printToPDF", {
                    "printBackground": True,
                    "paperWidth": 8.27,
                    "paperHeight": 11.69,
                    "marginTop": 0.8,
                    "marginBottom": 0.8,
                    "marginLeft": 0.8,
                    "marginRight": 0.8,
                    "displayHeaderFooter": False,
                    "preferCSSPageSize": True
                })

                data = res.get("result", {}).get("data")
                if data:
                    pdf_bytes = base64.b64decode(data)
                    with open(out_pdf, "wb") as f:
                        f.write(pdf_bytes)
                    print(f"Successfully compiled PDF: {out_pdf} ({len(pdf_bytes)} bytes)")
                    try:
                        with open(default_pdf, "wb") as f:
                            f.write(pdf_bytes)
                        print(f"Updated primary PDF: {default_pdf}")
                    except Exception as e:
                        print(f"Primary PDF is locked by external viewer; saved as {out_pdf}")

        asyncio.run(run_print())
    except Exception as e:
        print(f"PDF export warning: {e}")
    finally:
        proc.terminate()


def main():
    print(f"Reading markdown from: {MD_FILE}")
    with open(MD_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()

    print("Parsing Markdown to Academic HTML...")
    body_html = parse_markdown_to_html(md_text)
    full_html = build_full_html(body_html)

    print(f"Writing HTML to: {HTML_FILE}")
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(full_html)

    print("HTML conversion successful!")
    print("Exporting academic PDF...")
    export_pdf_cdp()


if __name__ == "__main__":
    main()

