#!/usr/bin/env python3
"""Turn the app's PrivacyPolicy.md into the site's privacy page.

usage: python3 tools/policy_to_html.py <PrivacyPolicy.md> privacy/index.html

Handles the same small Markdown the apps parse: a "# " title, "## " headings,
"- " list items and plain paragraphs. The paragraph holding "Last updated" is
styled as the date line, and email addresses become mailto links. Standard
library only.
"""
import html
import re
import sys

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy Policy · Deutsch des Tages</title>
<meta name="description" content="How Deutsch des Tages handles your data: the app doesn't collect any.">
<link rel="icon" type="image/png" href="../favicon.png">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main>
<a class="mark" href="../" aria-label="Deutsch des Tages, support">D<span>.</span></a>

{body}

<footer>
<p>Deutsch des Tages · <a href="../">Support</a> · <a href="./">Privacy Policy</a></p>
</footer>
</main>
</body>
</html>
"""

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def inline(text):
    text = html.escape(text, quote=False)
    return EMAIL.sub(lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', text)


def convert(markdown):
    out, para, items = [], [], []

    def flush():
        if para:
            text = " ".join(para)
            cls = ' class="meta"' if "Last updated" in text else ""
            out.append(f"<p{cls}>{inline(text)}</p>")
            para.clear()
        if items:
            out.append("<ul>\n" + "\n".join(f"<li>{inline(i)}</li>" for i in items) + "\n</ul>")
            items.clear()

    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            flush()
        elif line.startswith("# "):
            flush()
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            flush()
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if para:
                flush()
            items.append(line[2:])
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return "\n\n".join(out)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        body = convert(f.read())
    with open(dst, "w", encoding="utf-8") as f:
        f.write(PAGE.replace("{body}", body))
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
