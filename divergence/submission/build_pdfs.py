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

Link rewriting, before pandoc ever sees the text: a relative link like
`(results.md)` is correct in the repo (GitHub renders it, clicking it in
a browser works) but means nothing once pandoc/Edge have flattened it
into a PDF -- there is no "current directory" for a PDF reader to
resolve it against, so a judge clicking it gets nothing. Every relative
link is rewritten to an absolute `github.com/hariom-s27/divergence/blob/
main/...` URL, in memory, in a copy of the text piped to pandoc on
stdin -- the source .md files on disk are never touched, because the
relative form is the CORRECT form there. Image embeds (`![alt](path)`)
are deliberately left alone: rewriting one to a GitHub blob page (an
HTML page, not raw image bytes) would break the image inside the PDF,
not fix a link.

    python build_pdfs.py
"""
import os
import posixpath
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # divergence/
REPO_ROOT = os.path.dirname(ROOT)  # the actual git root -- origin is
# github.com/hariom-s27/divergence.git (confirmed via `git remote -v`,
# not assumed), and that repo's OWN root is this REPO_ROOT, not ROOT --
# divergence/ is a subfolder of it, same as it is locally. A link found
# inside divergence/SAMPLES.md pointing at "results.md" therefore
# resolves, on GitHub, to blob/main/divergence/results.md -- one level
# down from the repo root, not the repo root itself.

SOURCES = ["SAMPLES.md", "DOCUMENTATION.md"]

GITHUB_OWNER = "hariom-s27"
GITHUB_REPO = "divergence"
GITHUB_BRANCH = "main"

# Matches [text](target) but not ![alt](target) -- the negative
# lookbehind excludes image embeds on purpose, see the module docstring.
_LINK_RE = re.compile(r'(?<!!)\[([^\]]*)\]\(([^)\s]+)\)')


def _rewrite_link_target(target, source_dir_repo_rel):
    """target: the raw text between ( and ) in a markdown link.
    source_dir_repo_rel: POSIX path of the directory holding the source
    .md file, relative to the repo root (e.g. "divergence").

    Anchor-only links (#section) and already-absolute links (any
    scheme://, e.g. https://arxiv.org/...) are returned unchanged.
    Everything else is resolved relative to source_dir_repo_rel (real
    path resolution -- posixpath.normpath/join, not string
    concatenation, so "../README.md" from divergence/ correctly reaches
    the repo-root README.md instead of producing a bogus path) and
    rewritten to an absolute GitHub blob URL, with any #fragment
    preserved on the end."""
    path_part, has_hash, fragment = target.partition("#")
    if path_part == "" and has_hash:
        return target  # pure "#section" anchor -- untouched
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.\-]*://', path_part) or path_part.startswith("mailto:"):
        return target  # already absolute -- untouched
    if not path_part:
        return target
    resolved = posixpath.normpath(posixpath.join(source_dir_repo_rel, path_part))
    url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{resolved}"
    if has_hash:
        url += "#" + fragment
    return url


def rewrite_relative_links(md_text, source_dir_repo_rel):
    """Returns (rewritten_text, [(old_target, new_target), ...]) -- the
    list is every link this function actually changed, in the order
    encountered, for the caller to print. Links left untouched (anchors,
    already-absolute) are not included in that list."""
    changes = []

    def _sub(m):
        label, target = m.group(1), m.group(2)
        new_target = _rewrite_link_target(target, source_dir_repo_rel)
        if new_target != target:
            changes.append((target, new_target))
        return f"[{label}]({new_target})"

    return _LINK_RE.sub(_sub, md_text), changes

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

    # Repo-root-relative POSIX path of the directory every SOURCES file
    # actually lives in -- computed once, from the real filesystem
    # relationship between ROOT and REPO_ROOT, not hardcoded as the
    # string "divergence" (so this keeps working if this script is ever
    # moved relative to the repo root).
    source_dir_repo_rel = posixpath.normpath(
        os.path.relpath(ROOT, REPO_ROOT).replace(os.sep, "/")
    )

    all_changes = []
    try:
        for name in SOURCES:
            src = os.path.join(ROOT, name)
            stem = os.path.splitext(name)[0]
            html_path = os.path.join(HERE, stem + ".html")
            pdf_path = os.path.join(HERE, stem + ".pdf")

            with open(src, encoding="utf-8") as f:
                original_text = f.read()
            rewritten_text, changes = rewrite_relative_links(original_text, source_dir_repo_rel)
            all_changes.append((name, changes))

            # Piped to pandoc on stdin -- src on disk is never opened by
            # pandoc and never written to. -f markdown is required here:
            # pandoc infers the format from a filename's extension, which
            # stdin doesn't have.
            subprocess.run(
                [pandoc, "-f", "markdown", "-o", html_path, "--standalone",
                 "-H", style_path, "--metadata", "title=" + stem],
                input=rewritten_text.encode("utf-8"),
                cwd=ROOT, check=True,
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

    print("\nlinks rewritten (relative -> absolute GitHub URL), before pandoc:")
    total = 0
    for name, changes in all_changes:
        print(f"\n  {name}: {len(changes)} link(s) rewritten")
        for old, new in changes:
            print(f"    ({old}) -> ({new})")
            total += 1
    if total == 0:
        print("  none -- every link in every source was already absolute or anchor-only")


if __name__ == "__main__":
    main()
