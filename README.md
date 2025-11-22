# Git Commit Diff Analyzer (LCS-based)

A Streamlit app that compares two commits in a local git repository and computes per-file diffs using LCS/difflib.

### Link: https://git-commit-diff-analyzer-lcs-powered.streamlit.app/

## Quickstart

1. Create virtualenv and install:
   pip install -r requirements.txt

2. Run:
   streamlit run streamlit_app.py

3. Enter repo path and commits (e.g., HEAD~1 and HEAD), click Analyze.

## Features
- Per-file added/removed/unchanged counts
- Similarity %
- Unified diff view
- Exports: JSON / CSV

## For developers
- lcs_algo.py: LCS DP logic
- git_utils.py: GitPython helpers
- reporter.py: Report creation & export
