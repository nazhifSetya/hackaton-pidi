"""
PGABL - Tahap 4: Retrieval metrics (hit@k, MRR, NDCG@k) untuk eval RAG per-tier.

Ground truth per query = himpunan pasangan (pdf_source, pasal_number). Sebuah chunk
ter-retrieve dianggap RELEVAN jika (chunk.pdf_source, chunk.pasal) cocok dgn salah satu
pasangan ground truth. Matching by (pdf + pasal) -> tahan terhadap perubahan chunk_id.

Semua fungsi pure-Python (deterministic) -> di-verify lokal via scripts/11_verify_eval_metrics.py.
"""

from __future__ import annotations
import re
import math


def norm_pasal(s: str) -> str:
    """'Pasal 78' / 'pasal  78' -> '78'. Ambil digit pertama."""
    m = re.search(r"\d+", str(s))
    return m.group(0) if m else str(s).strip()


def parse_ground_truth(row: dict) -> set[tuple[str, str]]:
    """
    Row test-set -> set {(pdf, pasal_num)}. Dukung cross_pdf (comma-separated selaras).
    Contoh: pdf='UU_6_2023,PP_35_2021', pasal='Pasal 78,Pasal 31'
            -> {('UU_6_2023','78'), ('PP_35_2021','31')}
    """
    pdfs = [p.strip() for p in str(row["ground_truth_pdf"]).split(",")]
    pasals = [norm_pasal(p) for p in str(row["ground_truth_pasal"]).split(",")]
    return {(pdf, pas) for pdf, pas in zip(pdfs, pasals)}


def is_relevant(meta: dict, gt_set: set[tuple[str, str]]) -> bool:
    """Chunk (via metadata pdf_source+pasal) relevan kalau cocok salah satu gt pair."""
    return (meta.get("pdf_source"), norm_pasal(meta.get("pasal", ""))) in gt_set


def hit_at_k(retrieved: list[dict], gt_set: set, k: int) -> float:
    """1.0 kalau ada chunk relevan di Top-k, else 0.0."""
    return 1.0 if any(is_relevant(m, gt_set) for m in retrieved[:k]) else 0.0


def reciprocal_rank(retrieved: list[dict], gt_set: set) -> float:
    """1/rank chunk relevan pertama (0 kalau tak ada)."""
    for i, m in enumerate(retrieved):
        if is_relevant(m, gt_set):
            return 1.0 / (i + 1)
    return 0.0


def ndcg_at_k(retrieved: list[dict], gt_set: set, k: int) -> float:
    """
    NDCG@k dengan relevansi biner. IDCG = kondisi ideal (semua target relevan di posisi teratas),
    dibatasi min(|gt|, k).
    """
    dcg = sum(1.0 / math.log2(i + 2) for i, m in enumerate(retrieved[:k]) if is_relevant(m, gt_set))
    n_rel = min(len(gt_set), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(n_rel))
    return dcg / idcg if idcg > 0 else 0.0


def evaluate_queries(results: list[dict], k_list=(1, 3, 5), ndcg_k: int = 5) -> dict:
    """
    results: list of {"gt": set, "retrieved": [meta,...], "difficulty":.., "type":..}.
    Return metric rata-rata (overall) + breakdown by type & difficulty.
    """
    def _agg(subset):
        if not subset:
            return None
        out = {}
        for k in k_list:
            out[f"hit@{k}"] = round(sum(hit_at_k(r["retrieved"], r["gt"], k) for r in subset) / len(subset), 4)
        out["mrr"] = round(sum(reciprocal_rank(r["retrieved"], r["gt"]) for r in subset) / len(subset), 4)
        out[f"ndcg@{ndcg_k}"] = round(sum(ndcg_at_k(r["retrieved"], r["gt"], ndcg_k) for r in subset) / len(subset), 4)
        out["n"] = len(subset)
        return out

    report = {"overall": _agg(results), "by_type": {}, "by_difficulty": {}}
    for t in sorted({r.get("type") for r in results if r.get("type")}):
        report["by_type"][t] = _agg([r for r in results if r.get("type") == t])
    for d in sorted({r.get("difficulty") for r in results if r.get("difficulty")}):
        report["by_difficulty"][d] = _agg([r for r in results if r.get("difficulty") == d])
    return report
