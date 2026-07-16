"""
PGABL - Tahap 3c: relevance-threshold gating + DuckDuckGo fallback.

Alur: setelah reranker, kalau skor relevansi tertinggi < threshold -> query dianggap
di luar cakupan 4 dokumen -> ambil konteks dari web (DuckDuckGo) + WAJIB disclaimer.

Catatan robustness:
- Package `duckduckgo_search` sudah di-rename ke `ddgs` (2025) -> import ddgs dulu,
  fallback ke duckduckgo_search.
- Query TANPA operator `site:` (operator itu sering mengembalikan 0 hasil).
- DDG bisa rate-limit/kosong -> semua dibungkus try/except, return None kalau gagal.
"""

from __future__ import annotations
import math


def sigmoid(x: float) -> float:
    """Sigmoid stabil (skor reranker = logit -> probabilitas 0..1)."""
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def is_below_threshold(scores: list[float], threshold: float) -> bool:
    """True kalau skor relevansi tertinggi < threshold (trigger fallback)."""
    if not scores:
        return True
    return max(scores) < threshold


def ddg_search(query: str, max_results: int = 5, prefix: str = "regulasi Indonesia"):
    """
    Cari di DuckDuckGo. Return list {title, href, body} atau None kalau gagal/kosong.
    """
    DDGS = None
    try:
        from ddgs import DDGS as _D
        DDGS = _D
    except ImportError:
        try:
            from duckduckgo_search import DDGS as _D
            DDGS = _D
        except ImportError:
            return None
    q = f"{prefix} {query}".strip()
    try:
        with DDGS() as d:
            results = list(d.text(q, max_results=max_results))
    except Exception:
        return None
    return results or None


def build_web_context(results, disclaimer: str, max_snippets: int = 3):
    """Susun konteks dari hasil web + disclaimer di depan. None kalau tak ada hasil."""
    if not results:
        return None
    snippets = []
    for i, r in enumerate(results[:max_snippets]):
        body = (r.get("body") or "").strip()
        href = (r.get("href") or "").strip()
        title = (r.get("title") or "").strip()
        snippets.append(f"[Web {i+1}] {title}: {body} (sumber: {href})")
    return disclaimer.strip() + "\n\n" + "\n\n".join(snippets)
