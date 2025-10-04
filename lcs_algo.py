# lcs_algo.py
from typing import List, Tuple

def lcs_dp(a: List[str], b: List[str]) -> Tuple[int, List[Tuple[int,int]]]:
    """
    Compute length of LCS and the matching index pairs using DP.
    Returns: (lcs_length, list_of_matching_pairs_in_order)
    Matching pairs: list of (index_in_a, index_in_b)
    """
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return 0, []

    # DP table sized (m+1) x (n+1)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    # fill dp
    for i in range(1, m + 1):
        ai = a[i-1]
        for j in range(1, n + 1):
            if ai == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = dp[i-1][j] if dp[i-1][j] >= dp[i][j-1] else dp[i][j-1]

    # backtrack to get matched pairs
    i, j = m, n
    matches = []
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            matches.append((i-1, j-1))
            i -= 1
            j -= 1
        else:
            if dp[i-1][j] >= dp[i][j-1]:
                i -= 1
            else:
                j -= 1
    matches.reverse()
    return dp[m][n], matches


def compute_stats_using_lcs(lines_a: List[str], lines_b: List[str]) -> dict:
    lcs_len, matches = lcs_dp(lines_a, lines_b)
    added = len(lines_b) - lcs_len
    removed = len(lines_a) - lcs_len
    similarity = (lcs_len / max(1, max(len(lines_a), len(lines_b)))) * 100
    return {
        "len_a": len(lines_a),
        "len_b": len(lines_b),
        "lcs_len": lcs_len,
        "added": added,
        "removed": removed,
        "similarity": similarity,
        "matches": matches
    }
