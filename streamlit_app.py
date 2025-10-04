# streamlit_app.py
import streamlit as st
from git_utils import open_local_repo, list_files_changed_between_commits, get_file_content_at_commit, get_all_tracked_files_at_commit
from lcs_algo import compute_stats_using_lcs
from reporter import build_report, save_report_json, save_report_csv
from difflib import SequenceMatcher, unified_diff
import os
import pandas as pd
from typing import List

st.set_page_config(page_title="Commit Diff Analyzer", layout="wide")

st.title("🔍 Git Commit Diff Analyzer — LCS powered")
st.markdown("Enter a local git repository path (or use env) and two commit SHAs to compare.")

# Repo path entry
repo_path = st.text_input("Local Git repository path", value=".")
commit_a = st.text_input("Old commit SHA (or branch/tag)", value="")
commit_b = st.text_input("New commit SHA (or branch/tag)", value="")

use_all_files = st.checkbox("Compare all tracked files (not only changed files)", value=False)

if st.button("Analyze"):
    try:
        repo = open_local_repo(repo_path)
    except Exception as e:
        st.error(f"Could not open repo: {e}")
        st.stop()

    if not commit_a or not commit_b:
        st.error("Please provide both commit SHAs.")
        st.stop()

    # get list of files
    if use_all_files:
        files = get_all_tracked_files_at_commit(repo, commit_b)
    else:
        files = list_files_changed_between_commits(repo, commit_a, commit_b)

    if not files:
        st.info("No files changed between the commits (or no tracked files found).")
        st.stop()

    per_file_results = {}
    overall_matches = 0
    overall_len = 0
    files_display = []

    st.sidebar.markdown(f"**Comparing** {commit_a[:8]} → {commit_b[:8]}")
    st.sidebar.markdown(f"Files to analyze: {len(files)}")

    # iterate files and compute diffs
    for fname in files:
        try:
            content_a = get_file_content_at_commit(repo, commit_a, fname).splitlines()
        except Exception:
            content_a = []
        try:
            content_b = get_file_content_at_commit(repo, commit_b, fname).splitlines()
        except Exception:
            content_b = []

        # quick strategy: if files both empty, skip
        if not content_a and not content_b:
            continue

        # Use difflib SequenceMatcher for speed by default
        matcher = SequenceMatcher(None, content_a, content_b)
        matching_blocks = matcher.get_matching_blocks()
        lcs_len = sum(block.size for block in matching_blocks)
        added = len(content_b) - lcs_len
        removed = len(content_a) - lcs_len
        similarity = (lcs_len / max(1, max(len(content_a), len(content_b)))) * 100

        per_file_results[fname] = {
            "len_a": len(content_a),
            "len_b": len(content_b),
            "lcs_len": lcs_len,
            "added": added,
            "removed": removed,
            "similarity": round(similarity, 2)
        }
        overall_matches += lcs_len
        overall_len += max(len(content_a), len(content_b))
        files_display.append((fname, per_file_results[fname]))

    # show summary
    total_added = sum(r["added"] for r in per_file_results.values())
    total_removed = sum(r["removed"] for r in per_file_results.values())
    avg_similarity = (overall_matches / max(1, overall_len)) * 100

    st.header("Summary")
    st.metric("Files analyzed", len(per_file_results))
    st.metric("Total lines added", total_added)
    st.metric("Total lines removed", total_removed)
    st.metric("Overall similarity (%)", f"{round(avg_similarity,2)}")

    # show table
    df = pd.DataFrame([
        {
            "file": k,
            "len_a": v["len_a"],
            "len_b": v["len_b"],
            "lcs_len": v["lcs_len"],
            "added": v["added"],
            "removed": v["removed"],
            "similarity": v["similarity"]
        }
        for k, v in per_file_results.items()
    ]).sort_values(by="similarity", ascending=True)

    st.dataframe(df.reset_index(drop=True), use_container_width=True)

    # allow CSV/JSON export
    report = build_report(per_file_results, commit_a, commit_b)
    json_path = "commit_report.json"
    csv_path = "commit_report.csv"
    save_report_json(report, json_path)
    save_report_csv(per_file_results, csv_path)

    st.download_button("Download JSON report", data=open(json_path, "rb").read(), file_name=json_path, mime="application/json")
    st.download_button("Download CSV summary", data=open(csv_path, "rb").read(), file_name=csv_path, mime="text/csv")

    # show per-file diffs with collapsible UI
    st.header("Per-file details")
    for fname, stats in files_display:
        with st.expander(f"{fname} — similarity {stats['similarity']}% — +{stats['added']} / -{stats['removed']}"):
            content_a = []
            content_b = []
            try:
                content_a = get_file_content_at_commit(repo, commit_a, fname).splitlines()
            except:
                content_a = []
            try:
                content_b = get_file_content_at_commit(repo, commit_b, fname).splitlines()
            except:
                content_b = []

            # show unified diff text (human-readable)
            udiff = "\n".join(unified_diff(content_a, content_b, fromfile=f"{fname}@{commit_a[:8]}", tofile=f"{fname}@{commit_b[:8]}", lineterm=""))
            st.code(udiff, language="text")
