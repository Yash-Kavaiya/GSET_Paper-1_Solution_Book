"""Build the KDP wrap covers from the interior page count.

Paperback (KDP): cover = bleed + back + spine + front + bleed; height = trim + 2*bleed.
    spine = pages * 0.002252 in (white paper, B&W interior)
Hardcover (KDP case laminate): wrap of 0.591 in on every side (instead of bleed) and a
    hinge allowance; KDP publishes the exact hardcover spine for each page count in its
    cover-template calculator (https://kdp.amazon.com/cover-calculator). Pass it with
    --hardcover-spine to override the estimate below.
"""
import argparse
import subprocess
from pathlib import Path

import fitz

ROOT = Path(__file__).parent


def build(name, spine, bleed):
    tex = ROOT / "cover.tex"
    pre = (f"\\def\\spinewidth{{{spine:.4f}in}}\\def\\bleed{{{bleed:.4f}in}}"
           f"\\def\\trimw{{7in}}\\def\\trimh{{10in}}\\input{{{tex.name}}}")
    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"-jobname={name}", pre],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    w, h = fitz.open(ROOT / f"{name}.pdf")[0].rect.br
    print(f"{name}.pdf  spine={spine:.3f} in  size={w / 72:.3f} x {h / 72:.3f} in")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hardcover-spine", type=float, help="spine width in inches from the KDP calculator")
    a = ap.parse_args()
    pages = len(fitz.open(ROOT / "main.pdf"))
    print("interior pages:", pages)
    build("cover_paperback", pages * 0.002252, 0.125)
    hc_spine = a.hardcover_spine or pages * 0.002252 + 0.06  # board thickness estimate
    build("cover_hardcover", hc_spine, 0.591 + 0.25)          # wrap + hinge allowance


if __name__ == "__main__":
    main()
