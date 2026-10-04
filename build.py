#!/usr/bin/env python3
"""モンジムの公開ページ（プライバシーポリシー・利用規約・サポート）を作る。

    python3 build.py   # ~/dev/nushi/docs/store/*.md から docs/*.html を作り直す

文面の正は ~/dev/nushi/docs/store/privacy-policy.md と terms.md。プライバシーポリシーの
「付録」（App Store Connect の回答案）は公開ページに含めない。
"""
from __future__ import annotations

import html
import re
from pathlib import Path

SRC = Path.home() / "dev/nushi/docs/store"
OUT = Path(__file__).resolve().parent / "docs"
CONTACT = "matty.kenta323+apple@gmail.com"

CSS = """
:root { --bg: #f6f7f4; --ink: #1e2a44; --muted: #5b6474; --line: #d9dcd3; --accent: #1f7a5a; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); line-height: 1.85;
  font-family: "Hiragino Mincho ProN", "Yu Mincho", serif; }
main { max-width: 44rem; margin: 0 auto; padding: 3rem 1.25rem 5rem; }
h1 { font-size: 1.7rem; margin: 0 0 1.5rem; }
h2 { font-size: 1.15rem; margin: 2.5rem 0 0.75rem; padding-top: 1.25rem; border-top: 1px solid var(--line); }
p, li, td, th { font-family: "Hiragino Sans", "Yu Gothic", sans-serif; font-size: 0.95rem; }
a { color: var(--accent); }
table { width: 100%; border-collapse: collapse; margin: 1rem 0; display: block; overflow-x: auto; }
th, td { border: 1px solid var(--line); padding: 0.5rem 0.65rem; text-align: left; vertical-align: top; }
th { background: #eceee7; }
nav { font-family: "Hiragino Sans", "Yu Gothic", sans-serif; font-size: 0.85rem; margin-bottom: 2rem; }
nav a { margin-right: 1rem; }
footer { margin-top: 4rem; color: var(--muted); font-family: "Hiragino Sans", sans-serif; font-size: 0.8rem; }
"""

NAV = '<nav aria-label="ページ"><a href="./">サポート</a><a href="privacy.html">プライバシーポリシー</a><a href="terms.html">利用規約</a></nav>'


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{link(m.group(2))}">{m.group(1)}</a>', text)
    text = re.sub(r"(?<![\"=>])(https?://[^\s<）)]+)", r'<a href="\1">\1</a>', text)
    text = re.sub(r"(?<![\w.+-])([\w.+-]+@[\w-]+\.[\w.]+)", r'<a href="mailto:\1">\1</a>', text)
    return text


def link(target: str) -> str:
    return {"./privacy-policy.md": "privacy.html", "./terms.md": "terms.html"}.get(target, target)


def to_html(md: str) -> tuple[str, str]:
    """Returns (title, body html). Supports #/## headings, paragraphs, - lists, 1. lists and tables."""
    out: list[str] = []
    title = ""
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("# "):
            title = line[2:].strip()
            out.append(f"<h1>{inline(title)}</h1>")
            i += 1
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:].strip())}</h2>")
            i += 1
        elif line.startswith("#"):
            out.append(f"<h3>{inline(line.lstrip('#').strip())}</h3>")
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            out.append("<table><thead><tr>" + "".join(f'<th scope="col">{inline(c)}</th>' for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>")
        elif re.match(r"^(- |\d+\. )", line):
            ordered = not line.startswith("- ")
            items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||- |\d+\. )", lines[i]):
                para.append(lines[i].strip())
                i += 1
            if not para:  # a line no rule above consumed; never loop on it
                para.append(lines[i].strip())
                i += 1
            out.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")
    return title, "\n".join(out)


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | モンジム</title>
<style>{CSS}</style>
</head>
<body>
<main>
{NAV}
{body}
<footer>モンジム — 提供者: 赤松 健太</footer>
</main>
</body>
</html>
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    privacy = (SRC / "privacy-policy.md").read_text(encoding="utf-8").split("\n---\n")[0]
    terms = (SRC / "terms.md").read_text(encoding="utf-8").split("\n---\n")[0]
    for name, md in (("privacy.html", privacy), ("terms.html", terms)):
        title, body = to_html(md)
        (OUT / name).write_text(page(title, body), encoding="utf-8")
    support = f"""<h1>モンジム サポート</h1>
<p>モンジムは、筋トレの記録に応じて相棒が育っていく iOS アプリです。</p>
<h2>お問い合わせ</h2>
<p>不具合の報告、ご質問、ご要望は次のメールアドレスへお送りください。<br><a href="mailto:{CONTACT}">{CONTACT}</a></p>
<h2>よくあるご質問</h2>
<p><strong>購入したプランを復元したい</strong><br>設定画面の「購入を復元」から復元できます。</p>
<p><strong>サブスクリプションを解約したい</strong><br>iPhone の「設定」→ ご自身の名前 →「サブスクリプション」から解約できます。</p>
<p><strong>記録を消したい</strong><br>設定画面の「すべてのデータを削除」から、端末内の記録を削除できます。</p>
<h2>規約など</h2>
<ul><li><a href="privacy.html">プライバシーポリシー</a></li><li><a href="terms.html">利用規約</a></li></ul>"""
    (OUT / "index.html").write_text(page("サポート", support), encoding="utf-8")


if __name__ == "__main__":
    main()
