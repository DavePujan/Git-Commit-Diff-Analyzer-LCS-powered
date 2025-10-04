# reporter.py
import json
import csv
from typing import List, Dict

def build_report(per_file_results: Dict[str, dict], commit_a: str, commit_b: str) -> dict:
    total_added = sum(r.get("added", 0) for r in per_file_results.values())
    total_removed = sum(r.get("removed", 0) for r in per_file_results.values())
    summary = {
        "commit_a": commit_a,
        "commit_b": commit_b,
        "files": per_file_results,
        "total_added": total_added,
        "total_removed": total_removed,
        "total_files": len(per_file_results),
    }
    return summary

def save_report_json(report: dict, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

def save_report_csv(per_file_results: Dict[str, dict], path: str):
    # Flatten and save basic stats per file
    keys = ["file", "len_a", "len_b", "lcs_len", "added", "removed", "similarity"]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for fname, r in per_file_results.items():
            writer.writerow({
                "file": fname,
                "len_a": r.get("len_a"),
                "len_b": r.get("len_b"),
                "lcs_len": r.get("lcs_len"),
                "added": r.get("added"),
                "removed": r.get("removed"),
                "similarity": r.get("similarity")
            })
