# GSET Paper I: Solved Previous Year Papers (2002–2025)

A print-ready LaTeX book: 20 GSET Paper I papers, 1,070 questions. Each question has all four options, the answer from the official final key, and a full explanation. Diagrams and charts are redrawn in TikZ/pgfplots.

## Files for Amazon KDP

| File | Use |
|------|-----|
| `main.pdf` | Interior for **paperback and hardcover** (7 × 10 in, no bleed, B&W, fonts embedded) |
| `cover_paperback.pdf` | Full-wrap paperback cover (bleed 0.125 in, spine sized for white paper) |
| `cover_hardcover.pdf` | Hardcover case-wrap cover (an **estimate**; see below) |
| `kindle_cover.jpg` | Kindle eBook cover (1600 px wide) |

### Upload steps
1. **Paperback:** trim 7 × 10 in, black & white interior, white paper, no bleed, matte or glossy cover. Upload `main.pdf` and `cover_paperback.pdf`.
2. **Hardcover:** trim 7 × 10 in, case laminate. Before uploading, download KDP's hardcover cover template for **399 pages** (kdp.amazon.com/cover-calculator). Check the spine width against it, then run `python make_cover.py --hardcover-spine <width>` so the cover matches exactly.
3. **Kindle eBook:** the layout relies on tables and diagrams, so publish it as a *print replica*. Open `main.pdf` in **Kindle Create** ("PDF / print replica") and use `kindle_cover.jpg` as the cover.
4. Enter your ISBNs on the copyright page (`front/copyright.tex`), or let KDP assign free ISBNs and leave the placeholders blank.

## Rebuilding
```
python build.py            # data + explanations -> tex/*.tex
pdflatex main.tex          # run twice (for the table of contents)
pdflatex main.tex
python make_cover.py       # covers sized from the page count
```
You need MiKTeX or TeX Live, plus Python with PyMuPDF (`pip install pymupdf`).

## Structure
- `data/<paper>.json`: questions and options (English); `data/answer_keys.json` holds the official final keys
- `expl/<paper>.tex`: explanations and overrides (`%% Qn`, `%% Qn ctx|fig|q|opts|after|note`)
- `fig/`: a few figures cropped from the original booklets (symbol and figure series)
- `front/`: title page, copyright, preface, how-to-use, about GSET, quick revision

## Notes on the official keys
Answers always follow the GSET Agency's **final** key for the booklet series printed in each chapter. Where a key conflicts with the question, the book prints the official answer anyway and adds a "Note on the key". These papers have such notes: Jan 2002 (Q36, 37, 40, 46), Dec 2002 (Q33), Dec 2003 (Q5, 23, 28), July 2004 (Q7, 8, 10, 47, 50), July 2006 (Q36), Oct 2014 (Q29, 56), Dec 2013 (Q36, 45), Sept 2016 (Q60). Questions the agency dropped (Z/X) are flagged and still solved.
