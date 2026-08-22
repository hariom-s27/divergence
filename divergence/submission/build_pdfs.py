"""
build_pdfs.py -- regenerates the two Devpost-attachment PDFs (M1) from
their real source Markdown. No LaTeX: pandoc renders Markdown to a
small, self-contained styled HTML file (table borders/padding/wrapping,
so a judge on a phone can actually read a four-column table), then
Microsoft Edge's own headless --print-to-pdf turns that HTML into the
PDF. Zero toolchain beyond pandoc (already needed) and a browser every
Windows box already has -- no MiKTeX/TeX Live install.

--no-pdf-header-footer matters: without it, Chromium's print-to-pdf adds
a date/time header and a footer with the local file:// path to the temp
HTML file -- fine on screen, not something to hand a judge.

    python build_pdfs.py
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # divergence/

SOURCES = ["SAMPLES.md", "DOCUMENTATION.md"]

STYLE = """<style>
body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
       font-size: 11.5pt; line-height: 1.45; color: #1a1a1a; }
h1, h2, h3 { color: #111; }
code, pre { font-family: Consolas, "IBM Plex Mono", monospace; font-size: 0.85em; }
pre { background: #f4f4f4; padding: 0.6em; white-space: pre-wrap; word-wrap: break-word; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; table-layout: fixed; }
th, td { border: 1px solid #ccc; padding: 5px 8px; text-align: left;
         vertical-align: top; word-wrap: break-word; font-size: 9.5pt; }
th { background: #eee; }
a { color: #1a4b8c; }
blockquote { border-left: 3px solid #ccc; margin-left: 0; padding-left: 1em; color: #444; }
</style>"""


def _find_pandoc():
    p = shutil.which("pandoc")
    if p:
        return p
    guess = os.path.expandvars(r"%LOCALAPPDATA%\Pandoc\pandoc.exe")
    if os.path.exists(guess):
        return guess
    sys.exit("pandoc not found on PATH -- winget install JohnMacFarlane.Pandoc")


def _find_edge():
    for p in (
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ):
        if os.path.exists(p):
            return p
    sys.exit("msedge.exe not found in either Program Files location")


def main():
    pandoc = _find_pandoc()
    edge = _find_edge()

    style_path = os.path.join(HERE, "_pdf_style.html")
    with open(style_path, "w", encoding="utf-8") as f:
        f.write(STYLE)

    try:
        for name in SOURCES:
            src = os.path.join(ROOT, name)
            stem = os.path.splitext(name)[0]
            html_path = os.path.join(HERE, stem + ".html")
            pdf_path = os.path.join(HERE, stem + ".pdf")

            subprocess.run(
                [pandoc, src, "-o", html_path, "--standalone",
                 "-H", style_path, "--metadata", "title=" + stem],
                check=True,
            )
            subprocess.run(
                [edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                 "--print-to-pdf=" + pdf_path,
                 "file:///" + html_path.replace("\\", "/")],
                check=True,
            )
            os.remove(html_path)
            print("wrote", pdf_path, "(%d bytes)" % os.path.getsize(pdf_path))
    finally:
        os.remove(style_path)


if __name__ == "__main__":
    main()
