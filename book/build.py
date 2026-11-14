"""Assemble the GSET Paper-I solution book.

Inputs
  data/<pid>.json        questions: [{n, q, opts[4], context?}] (plain text)
  data/answer_keys.json  official final keys {pid: {booklet: "ABCD..."}}
  expl/<pid>.tex         explanations and raw-LaTeX overrides, in blocks:
                             %% Q<n>            explanation body
                             %% Q<n> ctx        passage/table/figure shown before the question
                             %% Q<n> fig        figure/table shown (centred) after the question text
                             %% Q<n> after      text shown after the figure, before the options
                             %% Q<n> q          replacement question text (raw LaTeX)
                             %% Q<n> opts       four options (raw LaTeX), one per line
                             %% Q<n> note       note about the official key (dropped / disputed)
Output
  tex/<pid>.tex, included by main.tex
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
EXPL = ROOT / "expl"
OUT = ROOT / "tex"

# Latest first: aspirants usually start with the most recent papers.
PAPERS = [
    ("nov25p1", "November 2025", "16 November 2025", "A", "19th GSET"),
    ("dec24p1", "December 2024", "1 December 2024", "A", "18th GSET"),
    ("nov23p1", "November 2023", "26 November 2023", "A", "17th GSET"),
    ("nov22p1", "November 2022", "6 November 2022", "A", "16th GSET"),
    ("dec21p1", "December 2021", "23 January 2022", "A", "15th GSET"),
    ("dec19p1", "December 2019", "29 December 2019", "A", "14th GSET"),
    ("sept18p1", "September 2018", "30 September 2018", "A", "13th GSET"),
    ("aug17p1", "August 2017", "27 August 2017", "A", "GSET 2017"),
    ("sept16p1", "September 2016", "25 September 2016", "A", "GSET 2016"),
    ("oct14p1", "October 2014", "October 2014", "A", "GSET 2014"),
    ("dec13p1", "December 2013", "December 2013", "A", "GSET 2013 (II)"),
    ("sept13p1", "September 2013", "September 2013", "A", "GSET 2013 (I)"),
    ("oct11p1", "October 2011", "October 2011", "A", "GSET 2011"),
    ("oct10p1", "October 2010", "October 2010", "A", "GSET 2010"),
    ("dec08p1", "December 2008", "7 December 2008", "C", "GSET 2008"),
    ("jy06p1", "July 2006", "July 2006", "A", "GSET 2006"),
    ("jy04p1", "July 2004", "25 July 2004", "C", "GSET 2004"),
    ("dec03p1", "December 2003", "7 December 2003", "C", "GSET 2003"),
    ("dec02p1", "December 2002", "1 December 2002", "B", "GSET 2002 (II)"),
    ("jan02p1", "January 2002", "20 January 2002", "B", "GSET 2002 (I)"),
]

_ESC = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def esc(s: str) -> str:
    """Escape plain text for LaTeX, leaving $...$ math segments untouched."""
    parts = re.split(r"(\$[^$]+\$)", s)
    return "".join(p if p.startswith("$") and p.endswith("$") and len(p) > 2 else esc_text(p) for p in parts)


def esc_text(s: str) -> str:
    s = "".join(_ESC.get(c, c) for c in s)
    s = s.replace("\u2018", "`").replace("\u2019", "'").replace("\u201c", "``").replace("\u201d", "''")
    s = s.replace("\u2013", "--").replace("\u2014", "---").replace("\u2026", r"\ldots{}")
    s = s.replace("\u00d7", r"$\times$").replace("\u00f7", r"$\div$").replace("\u2192", r"$\rightarrow$")
    s = s.replace("\u2264", r"$\le$").replace("\u2265", r"$\ge$").replace("\u00b0", r"\textdegree{}")
    s = s.replace("\u221a", r"$\surd$").replace("\u00bd", r"$\frac12$").replace("\u2212", "--")
    s = re.sub(r"(?<!\w)\.\.\.+", r"\\ldots{}", s)
    s = re.sub(r"(\\_){3,}", r"\\blank{}", s)
    s = s.replace("₹", "Rs. ").replace("\n", "\\newline ")
    bad = {c for c in s if ord(c) > 0x7F and c not in "éèüöä"}
    if bad:
        print("  warning: unsupported characters", sorted(bad), "in:", s[:60].encode("ascii", "replace"))
        s = "".join("?" if c in bad else c for c in s)
    return s


def parse_expl(pid):
    """Return {n: {kind: text}} from expl/<pid>.tex."""
    path = EXPL / f"{pid}.tex"
    blocks = {}
    if not path.exists():
        return blocks
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^%%\s*Q(\d+)\s*(\w*)\s*$", line)
        if m:
            cur = (int(m.group(1)), m.group(2) or "expl")
            blocks.setdefault(cur[0], {})[cur[1]] = []
            continue
        if cur:
            blocks[cur[0]][cur[1]].append(line)
    return {n: {k: "\n".join(v).strip() for k, v in d.items()} for n, d in blocks.items()}


def opts_layout(opts):
    if any("\\tikz" in o or "\\includegraphics" in o or "\\die" in o for o in opts):
        return "optsfour"
    plain = [re.sub(r"\\[a-zA-Z]+|[{}$]", "", o) for o in opts]
    longest = max(len(o) for o in plain)
    if longest <= 14:
        return "optsfour"
    if longest <= 38:
        return "optstwo"
    return "optsone"


_HEADER = re.compile(r"^(List|Column|Section|Set|Group)\s*[-–]?\s*(I{1,2}|A|B|1|2|X|Y)\b.*$|^[A-Z][\w .()'/-]{0,40}:$", re.I)
_ITEM = re.compile(r"^\(?([0-9]{1,2}|[a-hA-H]|i{1,3}|iv|v|vi|I{1,3}|IV|V|VI)[.)]\s+\S")


_INLINE_ITEM = re.compile(r"\s(?=\((?:[1-9]|I{1,3}|IV|V|VI|i{1,3}|iv|v|vi|[a-f])\)\s)")
_INLINE_HEAD = re.compile(r"\s(?=(?:Statements?|Conclusions?|Arguments?|Assumptions?|Codes?)\s*:)"
                          r"|(?<=[.:?])\s(?=(?:Choose|Select|Which of the|The correct|In the light|In light|Identify the correct)\b)")


def split_inline_items(s: str) -> str:
    """Put inline enumerations such as '(1) ... (2) ...' on separate lines."""
    if len(re.findall(r"\((?:[1-9]|I{1,3}|IV|i{1,3}|iv|[a-f])\)\s", s)) < 2:
        return s
    s = _INLINE_ITEM.sub("\n", s)
    return _INLINE_HEAD.sub("\n", s)


def format_question(raw: str) -> str:
    """Escape a question; render 'match the following' lists as a two-column table."""
    if "\n" not in raw:
        raw = split_inline_items(raw)
    lines = [l.strip() for l in raw.split("\n")]
    lines = [l for l in lines if l]
    heads = [i for i, l in enumerate(lines) if _HEADER.match(l) and not _ITEM.match(l)]
    for a in range(len(heads) - 1):
        h1, h2 = heads[a], heads[a + 1]
        # a header may carry a one-line subtitle such as "(Software)"
        s1 = h1 + 1 if h1 + 1 < h2 and not _ITEM.match(lines[h1 + 1]) else h1
        left = lines[s1 + 1:h2]
        if len(left) < 3 or not all(_ITEM.match(l) for l in left):
            continue
        s2 = h2 + 1 if h2 + 1 < len(lines) and not _ITEM.match(lines[h2 + 1]) else h2
        right = []
        j = s2 + 1
        while j < len(lines) and _ITEM.match(lines[j]) and len(right) < len(left):
            right.append(lines[j])
            j += 1
        if len(right) != len(left):
            continue
        head1 = " ".join(lines[h1:s1 + 1]).rstrip(":")
        head2 = " ".join(lines[h2:s2 + 1]).rstrip(":")
        rows = [f"{esc(x)} & {esc(y)}\\\\" for x, y in zip(left, right)]
        table = ("\\par\\smallskip\\begin{tabularx}{\\linewidth}{@{}>{\\raggedright\\arraybackslash}X"
                 ">{\\raggedright\\arraybackslash}X@{}}\\toprule\n"
                 f"\\textbf{{{esc(head1)}}} & \\textbf{{{esc(head2)}}}\\\\\\midrule\n"
                 + "\n".join(rows) + "\n\\bottomrule\\end{tabularx}\\par\\smallskip\n")
        pre = esc("\n".join(lines[:h1]))
        post = esc("\n".join(lines[j:]))
        return pre + table + post
    return esc(raw)


def key_rows(key):
    cells = [f"\\kcell{{{i + 1}}}{{{a}}}" for i, a in enumerate(key)]
    rows = [" & ".join(cells[i:i + 10]) for i in range(0, len(cells), 10)]
    return " \\\\\n".join(rows)


def build_paper(pid, title, date, booklet, edition, keys):
    qs = json.loads((DATA / f"{pid}.json").read_text(encoding="utf-8"))
    key = keys[pid][booklet]
    ex = parse_expl(pid)
    missing = []
    out = [
        f"\\paperchapter{{{title}}}{{{date}}}{{{booklet}}}{{{len(qs)}}}{{{edition}}}",
        "\\keytable{" + key_rows(key) + "}",
    ]
    for q in qs:
        n = q["n"]
        e = ex.get(n, {})
        ans = key[n - 1]
        qtext = e.get("q") or format_question(q["q"])
        if "opts" in e:
            opts = [o.strip() for o in e["opts"].splitlines() if o.strip()]
        else:
            opts = [esc(o) for o in q["opts"]]
        if len(opts) != 4:
            sys.exit(f"{pid} Q{n}: expected 4 options, got {len(opts)}")
        if "ctx" in e:
            out.append(f"\\begin{{context}}\n{e['ctx']}\n\\end{{context}}")
        elif q.get("context"):
            out.append(f"\\begin{{context}}\n{esc(q['context'])}\n\\end{{context}}")
        out.append(f"\\begin{{question}}{{{n}}}")
        out.append("{" + qtext + "\\par}")
        if "fig" in e:
            out.append(f"\\qfigure{{{e['fig']}}}")
        if "after" in e:
            out.append(e["after"])
        out.append(f"\\{opts_layout(opts)}" + "".join(f"{{{o}}}" for o in opts))
        if ans in "ABCD":
            out.append(f"\\answer{{{ans}}}{{{opts['ABCD'.index(ans)]}}}")
        else:
            out.append("\\dropped{}")
        if "note" in e:
            out.append(f"\\keynote{{{e['note']}}}")
        body = e.get("expl")
        if not body:
            missing.append(n)
            body = "\\textit{Explanation to be added.}"
        out.append(f"\\begin{{explain}}\n{body}\n\\end{{explain}}")
        out.append("\\end{question}\n")
    (OUT / f"{pid}.tex").write_text("\n".join(out), encoding="utf-8")
    return len(qs), missing


def main():
    OUT.mkdir(exist_ok=True)
    keys = json.loads((DATA / "answer_keys.json").read_text())
    only = set(sys.argv[1:])
    total = 0
    includes = []
    for pid, title, date, booklet, edition in PAPERS:
        if not (DATA / f"{pid}.json").exists():
            print(f"{pid}: no data yet")
            continue
        includes.append(f"\\input{{tex/{pid}}}")
        if only and pid not in only:
            continue
        n, missing = build_paper(pid, title, date, booklet, edition, keys)
        total += n
        flag = f"  MISSING EXPL: {missing}" if missing else ""
        print(f"{pid}: {n} questions{flag}")
    (OUT / "papers.tex").write_text("\n".join(includes) + "\n", encoding="utf-8")
    print("total", total)


if __name__ == "__main__":
    main()
