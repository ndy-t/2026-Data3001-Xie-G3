# Final report — LaTeX project

`main.pdf` is the compiled report: 25 A4 pages, including references, the AI reflection and the appendix (limit: 30).

## Structure

```
report/
├── main.tex                  # preamble, title block, section includes
├── sections/                 # 00_summary … 10_ai_reflection
├── appendix/A_supplementary.tex
├── references.bib            # all DOIs verified via Crossref/DataCite
├── figures/                  # copies of selected image/report/*.png (originals untouched)
│   └── generated/            # figures produced by scripts/make_figures.py
├── scripts/make_figures.py   # regenerates figures/generated/ from saved outputs only
├── main.pdf                  # compiled report
├── verification_note.md      # source of every key number + open issues
└── figure_table_inventory.md
```

## Compile

**Overleaf:** upload the whole `report/` folder (zip it first) and set the compiler to pdfLaTeX. BibTeX runs automatically. All packages are in standard TeX Live.

**Locally:** use `latexmk -pdf main.tex`, or with [Tectonic](https://tectonic-typesetting.github.io) run `tectonic main.tex`. Tectonic was used to build `main.pdf`.

## Regenerate the generated figures

Run from the repository root, in any environment with `numpy`, `pandas`, `pyarrow` and `matplotlib`:

```bash
python report/scripts/make_figures.py            # all figures
python report/scripts/make_figures.py traj joint # selected stages
```

Stages: `test spatial region drogue traj joint sst motion boot temporal`.

The script reads only `models/final_test_comparison.csv`, `data/processed/report_test_predictions.parquet`, `data/processed/modelling_dataset_final.parquet` and `data/processed/gulf_stream_trajectories.parquet`. Every re-plot asserts agreement with the values printed in notebook 08 (e.g. 145 spatial cells and 73,214 forecasts, trajectory panel medians, joint-regime and SST tables, yearly medians) and prints the derived values used in the report. It trains and evaluates no model.

## Before submission (see `verification_note.md` §5)

- Replace the author placeholders and the `[name to be confirmed]` industry-partner placeholder in `main.tex`.
- The repository `README.md` now documents the final workflow, but notebook 08, `models/`, `report/` and the large processed files are not yet in Git, and package versions are not pinned. Commit or share them, and pin versions, so the README instructions can actually be followed (rubric: 20%).
