"""Generate the API reference of vocabtool as Markdown (docs/api/), from the docstrings in the code.

The pages render on GitHub as they are, and can be exported from there (or converted with pandoc). Only the
Python standard library is used and the code is read with ast, not imported, so it runs without the project's
dependencies (also in the GitHub workflow .github/workflows/docs.yml).

    python tools/gen_api_docs.py           write docs/api/
    python tools/gen_api_docs.py --check   exit 1 if docs/api/ is not up to date

Docstrings follow the Google style: a summary line, a blank line, more text, and sections such as Args:,
Returns:, Raises: and Attributes: with indented "name: text" entries.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "vocabtool"
OUT = ROOT / "docs" / "api"
SECTIONS = ("Args", "Arguments", "Returns", "Raises", "Attributes", "Example", "Examples", "Yields", "Note")


def _is_block(lines: list[str]) -> bool:
    """True for usage text or examples: column-aligned text, or indented lines that are not a Markdown list."""
    aligned = any(re.search(r"\S {3,}\S", l) for l in lines)
    indented = any(l.startswith(("    ", "\t")) for l in lines)
    return aligned or (indented and not lines[0].lstrip().startswith("- "))


def render_doc(doc: str | None) -> str:
    """Docstring -> Markdown.

    The docstring is read paragraph by paragraph (separated by blank lines). A paragraph that starts with a Google
    section (Args:, Returns:, ...) becomes a bold heading with a list of "name: text" entries; a paragraph with
    indented or column-aligned lines (usage text, examples) is kept as written in a text block; any other paragraph
    is plain Markdown text.
    """
    if not doc:
        return "_No description._\n"
    out = []
    for para in re.split(r"\n\s*\n", doc.strip("\n")):
        lines = para.splitlines()
        head = lines[0].strip()
        if head.endswith(":") and head[:-1] in SECTIONS:
            out += [f"**{head[:-1]}**", ""]
            entries = []
            for line in lines[1:]:
                m = re.match(r"\s+(\*{0,2}[\w.]+(?: \([^)]*\))?):\s*(.*)", line)
                if m and head[:-1] in ("Args", "Arguments", "Attributes", "Raises") and len(line) - len(line.lstrip()) <= 4:
                    entries.append(f"- `{m.group(1)}`: {m.group(2)}")
                elif entries:
                    entries[-1] += " " + line.strip()              # continuation of an entry
                else:
                    entries.append(line.strip())
            out += entries + [""]
        elif _is_block(lines):
            out += ["```text", *lines, "```", ""]
        else:
            out += lines + [""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out).strip() + "\n")


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """def name(args) -> return, as in the source."""
    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{node.name}({ast.unparse(node.args)}){ret}"


def _line_comments(src: str) -> dict[int, str]:
    """{line number: comment text} for comments that end a line of code (strings with # are not comments)."""
    import io
    import tokenize
    out = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT and tok.line[:tok.start[1]].strip():
            out[tok.start[0]] = tok.string[1:].strip()
    return out


def constants(tree: ast.Module, lines: list[str]) -> list[tuple[str, str]]:
    """Public module-level constants (UPPER_CASE) with the comment lines above them or at the end of the line."""
    trailing = _line_comments("\n".join(lines) + "\n")
    out = []
    for n in tree.body:
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            names = [t.id for t in targets if isinstance(t, ast.Name) and t.id.isupper() and not t.id.startswith("_")]
            if not names:
                continue
            comment, i = [], n.lineno - 2
            while i >= 0 and lines[i].lstrip().startswith("#") and not re.match(r"#\s*-{5,}", lines[i].lstrip()):
                comment.insert(0, lines[i].lstrip()[1:].strip())      # a "# -----" divider ends the comment
                i -= 1
            if n.lineno in trailing:
                comment.append(trailing[n.lineno])
            out.append((", ".join(names), " ".join(comment)))
    return out


def module_page(path: Path) -> tuple[str, str]:
    """Markdown page of one module, and the first line of its docstring (for the index)."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    name = "vocabtool" if path.stem == "__init__" else f"vocabtool.{path.stem}"
    doc = ast.get_docstring(tree)
    summary = (doc or "").strip().splitlines()[0] if doc else ""
    md = [f"# `{name}`", "", f"Source: [`{path.relative_to(ROOT).as_posix()}`](../../{path.relative_to(ROOT).as_posix()})", "",
          render_doc(doc)]
    consts = constants(tree, src.splitlines())
    if consts:
        md += ["## Constants", "", "| Name | Meaning |", "| --- | --- |"]
        md += [f"| `{n}` | {c.replace('|', '/') or '–'} |" for n, c in consts]
        md.append("")
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
    funcs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_")]
    for c in classes:
        md += [f"## class `{c.name}`", "", render_doc(ast.get_docstring(c))]
        for m in c.body:
            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("_"):
                prop = any(isinstance(d, ast.Name) and d.id == "property" for d in m.decorator_list)
                title = f"`{c.name}.{m.name}`" + (" (property)" if prop else f": `{signature(m)}`")
                md += [f"### {title}", "", render_doc(ast.get_docstring(m))]
    if funcs:
        md += ["## Functions", ""]
        for f in funcs:
            md += [f"### `{f.name}`", "", "```python", f"def {signature(f)}", "```", "", render_doc(ast.get_docstring(f))]
    private = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name.startswith("_")]
    if private:
        md += ["## Internal helpers", "", "Documented in the source: " + ", ".join(f"`{p}`" for p in private) + ".", ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(md)).rstrip() + "\n", summary


def build() -> dict[str, str]:
    """{file name in docs/api: content} for all modules and the index."""
    files, rows = {}, []
    for path in sorted(PACKAGE.glob("*.py")):
        if path.stem == "__main__":
            continue
        page, summary = module_page(path)
        fname = "vocabtool.md" if path.stem == "__init__" else f"{path.stem}.md"
        files[fname] = page
        rows.append((path.stem, fname, summary))
    index = ["# vocabtool API reference", "",
             "Generated from the docstrings by `python tools/gen_api_docs.py`; do not edit these pages by hand.",
             "Command-line use is described in the [README](../../README.md); the command reference is in [cli](cli.md).", "",
             "| Module | Purpose |", "| --- | --- |"]
    index += [f"| [{'vocabtool' if s == '__init__' else s}]({f}) | {d.replace('|', '/')} |" for s, f, d in rows]
    files["README.md"] = "\n".join(index) + "\n"
    return files


def main(argv: list[str]) -> int:
    """Write docs/api/, or with --check report whether it is up to date."""
    files = build()
    if "--check" in argv:
        stale = [f for f, c in files.items() if not (OUT / f).exists() or (OUT / f).read_text(encoding="utf-8") != c]
        extra = [p.name for p in OUT.glob("*.md") if p.name not in files] if OUT.exists() else []
        if stale or extra:
            print("docs/api is not up to date; run: python tools/gen_api_docs.py")
            for f in stale + extra:
                print("  ", f)
            return 1
        print("docs/api is up to date")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("*.md"):
        if p.name not in files:
            p.unlink()
    for f, c in files.items():
        (OUT / f).write_text(c, encoding="utf-8")
    print(f"{len(files)} pages written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
