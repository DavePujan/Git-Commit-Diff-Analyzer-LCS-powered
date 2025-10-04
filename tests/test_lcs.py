# tests/test_lcs.py
from lcs_algo import lcs_dp

def test_lcs_basic():
    a = ["a","b","c","d"]
    b = ["a","x","c","d"]
    lcs_len, matches = lcs_dp(a,b)
    assert lcs_len == 3
    assert matches == [(0,0),(2,2),(3,3)]
