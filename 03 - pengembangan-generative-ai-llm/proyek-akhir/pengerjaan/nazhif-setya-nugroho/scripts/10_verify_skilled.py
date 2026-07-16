"""
PGABL Tahap 3b - VERIFY-FIRST lokal untuk logika non-model:
  parent-store (de-overlap), BM25 search, query router, RRF fusion, citation.

Jalankan: <venv>/bin/python scripts/10_verify_skilled.py
Baca hasil: outputs/samples/skilled_verify.json (via Read tool).
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.rag.retriever import (
    tokenize, route_query, reciprocal_rank_fusion, build_parent_store,
    BM25Index, format_citation, parent_key_of,
)

PROCESSED = ROOT / "data" / "processed" / "pdfs"
SAMPLES = ROOT / "outputs" / "samples"
PDFS = ["PP_5_2021", "PP_35_2021", "PP_51_2023", "UU_6_2023"]
COLLECTION_NAMES = ["pp_5_2021", "pp_35_2021", "pp_51_2023"] + \
                   [f"uu_6_2023_klaster_{k}" for k in range(1, 16)]


def load_all_chunks():
    out = {}
    for p in PDFS:
        out[p] = json.loads((PROCESSED / p / "chunks.json").read_text(encoding="utf-8"))
    return out


def main():
    SAMPLES.mkdir(parents=True, exist_ok=True)
    all_chunks = load_all_chunks()
    flat = [c for chunks in all_chunks.values() for c in chunks]
    report = {}

    # ---- 1. Parent store: de-overlap reconstruction ----
    store = build_parent_store(all_chunks, overlap=100)
    # ambil parent yg punya >1 child (pasal panjang ke-split) untuk uji rekonstruksi
    multi = [(k, v) for k, v in store.items() if v["n_children"] > 1]
    checks = []
    for pkey, parent in multi[:5]:
        # child pertama utk parent ini -> length blok asli
        first_child = next(c for chunks in all_chunks.values() for c in chunks
                           if parent_key_of(c["chunk_id"]) == pkey and c["sub_index"] == 0)
        checks.append({
            "parent_id": pkey,
            "n_children": parent["n_children"],
            "parent_text_len": len(parent["text"]),
            "original_block_len": first_child["length"],
            "reconstruct_exact": len(parent["text"]) == first_child["length"],
            "parent_longer_than_child": len(parent["text"]) > len(first_child["text"]),
        })
    report["parent_store"] = {
        "total_parents": len(store),
        "multi_child_parents": len(multi),
        "reconstruction_checks": checks,
        "all_exact": all(c["reconstruct_exact"] for c in checks),
    }

    # ---- 2. Query router ----
    router_tests = {}
    for q in ["Berapa upah kerja lembur staf admin?",
              "Apa itu Nomor Induk Berusaha (NIB)?",
              "Bagaimana formula upah minimum?",
              "Resep rendang padang enak"]:
        cols, theme = route_query(q, COLLECTION_NAMES)
        router_tests[q] = {"theme": theme, "n_collections": len(cols),
                           "collections": cols if len(cols) <= 6 else f"ALL({len(cols)})"}
    report["router"] = router_tests

    # ---- 3. BM25 search ----
    bm25 = BM25Index(flat)
    bm25_tests = {}
    for q, expect in [("upah kerja lembur jam pertama", ("PP_35_2021", "31")),
                      ("Nomor Induk Berusaha NIB", ("PP_5_2021", None)),
                      ("uang kompensasi PKWT", ("PP_35_2021", None))]:
        top = bm25.search(q, top_n=5)
        top_meta = []
        for cid in top:
            c = next(x for x in flat if x["chunk_id"] == cid)
            top_meta.append({"chunk_id": cid, "pdf": c["pdf_source"], "pasal": c["pasal"]})
        found_pdf = any(m["pdf"] == expect[0] for m in top_meta)
        found_pasal = (expect[1] is None) or any(m["pasal"] == expect[1] for m in top_meta)
        bm25_tests[q] = {"expect_pdf": expect[0], "expect_pasal": expect[1],
                         "found_pdf": found_pdf, "found_pasal": found_pasal, "top5": top_meta}
    report["bm25"] = bm25_tests

    # ---- 4. RRF fusion (synthetic + real) ----
    # synthetic: item X peringkat tinggi di dua-duanya harus menang
    dense = ["A", "B", "C", "D"]
    sparse = ["C", "A", "E", "F"]
    fused = reciprocal_rank_fusion([dense, sparse], k=60)
    report["rrf_synthetic"] = {
        "dense": dense, "sparse": sparse,
        "fused_top": [i for i, _ in fused[:4]],
        "A_beats_D": [i for i, _ in fused].index("A") < [i for i, _ in fused].index("D"),
        "C_top1": fused[0][0] == "C",  # C = rank0 dense + rank0 sparse -> tertinggi
    }

    # ---- 5. Citation format ----
    sample_meta = {"pdf_source": "UU_6_2023", "klaster_label": "Ketenagakerjaan",
                   "bab": "IV", "pasal": "80"}
    report["citation_example"] = format_citation(1, sample_meta)

    (SAMPLES / "skilled_verify.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("parent all_exact:", report["parent_store"]["all_exact"],
          "| BM25 lembur->PP35 Pasal31:", report["bm25"]["upah kerja lembur jam pertama"]["found_pasal"],
          "| RRF C_top1:", report["rrf_synthetic"]["C_top1"])
    print("Report: outputs/samples/skilled_verify.json")


if __name__ == "__main__":
    main()
