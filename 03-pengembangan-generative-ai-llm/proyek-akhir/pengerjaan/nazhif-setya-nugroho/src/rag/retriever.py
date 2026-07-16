"""
PGABL - Retriever layer (Tahap 3b Skilled).

Komponen (semua modular, portable ke domain lain):
  - tokenize + BM25Index    : sinyal sparse (exact-match: nomor pasal, istilah "PKWT")
  - route_query             : keyword -> klaster/collection kandidat (metadata filtering)
  - reciprocal_rank_fusion  : gabung ranking BM25 + Dense (RRF)
  - build_parent_store      : rekonstruksi teks pasal UTUH (parent) dari sub-chunk (child)
  - format_citation         : label sitasi [Sumber N: PDF - BAB/Klaster - Pasal]

Dense retrieval (BGE-M3 + ChromaDB) dijalankan di notebook (butuh GPU); modul ini
menyediakan logika non-model yang di-verify lokal via scripts/10_verify_skilled.py.
"""

from __future__ import annotations
import re
from collections import defaultdict
from typing import Optional


# ==================== Tokenizer untuk BM25 ====================
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Tokenisasi sederhana: lowercase + ambil token alfanumerik."""
    return _TOKEN_RE.findall(text.lower())


# ==================== Query routing (metadata filtering) ====================
# Keyword tema -> collection kandidat. PP dipetakan by topik:
#   PP_5_2021 = perizinan, PP_35_2021 = ketenagakerjaan, PP_51_2023 = pengupahan.
ROUTING_RULES = [
    {
        "theme": "ketenagakerjaan",
        "keywords": ["lembur", "upah", "pkwt", "pkwtt", "phk", "pemutusan hubungan kerja",
                     "pesangon", "cuti", "pekerja", "buruh", "serikat", "alih daya",
                     "outsourcing", "waktu kerja", "pengupahan", "tenaga kerja",
                     "jaminan sosial", "perjanjian kerja", "hubungan kerja"],
        "collections": ["pp_35_2021", "pp_51_2023", "uu_6_2023_klaster_4"],
    },
    {
        "theme": "perizinan_investasi",
        "keywords": ["izin", "perizinan", "nib", "oss", "kbli", "risiko", "berusaha",
                     "penanaman modal", "investasi", "lingkungan hidup", "bangunan gedung",
                     "tata ruang", "amdal"],
        "collections": ["pp_5_2021", "uu_6_2023_klaster_3", "uu_6_2023_klaster_6"],
    },
    {
        "theme": "pengupahan",
        "keywords": ["upah minimum", "ump", "umk", "umr", "formula upah",
                     "penyesuaian upah", "dewan pengupahan"],
        "collections": ["pp_51_2023", "uu_6_2023_klaster_4"],
    },
]


def route_query(query: str, all_collections: list[str]) -> tuple[list[str], Optional[str]]:
    """
    Return (collections_target, theme). Kalau ada keyword match -> collection kandidat
    tema tsb (metadata filter). Kalau tidak ada match -> semua collection (fallback-to-all).
    """
    low = query.lower()
    matched: list[str] = []
    theme = None
    for rule in ROUTING_RULES:
        if any(kw in low for kw in rule["keywords"]):
            theme = theme or rule["theme"]
            for c in rule["collections"]:
                if c in all_collections and c not in matched:
                    matched.append(c)
    if not matched:
        return list(all_collections), None
    return matched, theme


# ==================== Reciprocal Rank Fusion ====================
def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """
    Gabung beberapa ranked list (list of ids urut relevansi) via RRF.
    Skor(id) = sum_over_lists 1 / (k + rank), rank 0-based.
    Return list (id, score) urut skor menurun.
    """
    scores: dict[str, float] = defaultdict(float)
    for lst in ranked_lists:
        for rank, item_id in enumerate(lst):
            scores[item_id] += 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ==================== Parent-Child ====================
def parent_key_of(chunk_id: str) -> str:
    """child chunk_id -> parent_key (buang suffix _sub{j})."""
    return chunk_id.rsplit("_sub", 1)[0]


def build_parent_store(all_chunks: dict[str, list[dict]], overlap: int = 100) -> dict[str, dict]:
    """
    Bangun 'parent' = teks pasal UTUH dari sub-chunk (child). Rekonstruksi de-overlap:
    parent = sub0 + sub1[overlap:] + sub2[overlap:] + ...  (kebalikan sliding-window split,
    jadi parent == blok pasal asli). Untuk pasal 1-chunk, parent == child.

    Return {parent_key: {parent_id, text, pdf_source, pasal, bab, klaster_label, n_children}}.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for chunks in all_chunks.values():
        for c in chunks:
            groups[parent_key_of(c["chunk_id"])].append(c)

    store: dict[str, dict] = {}
    for pkey, g in groups.items():
        g = sorted(g, key=lambda x: x["sub_index"])
        text = g[0]["text"]
        for c in g[1:]:
            text += c["text"][overlap:] if len(c["text"]) > overlap else ""
        first = g[0]
        store[pkey] = {
            "parent_id": pkey,
            "text": text,
            "pdf_source": first["pdf_source"],
            "pasal": first["pasal"],
            "bab": first.get("bab"),
            "klaster_label": first.get("klaster_label"),
            "n_children": len(g),
        }
    return store


# ==================== BM25 index ====================
class BM25Index:
    """BM25Okapi di atas seluruh chunk (global). Filter collection via allowed_ids."""

    def __init__(self, chunks: list[dict]):
        from rank_bm25 import BM25Okapi
        self.chunks = chunks
        self.ids = [c["chunk_id"] for c in chunks]
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])

    def search(self, query: str, top_n: int = 20, allowed_ids: Optional[set] = None) -> list[str]:
        scores = self.bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        out: list[str] = []
        for i in order:
            cid = self.ids[i]
            if allowed_ids is not None and cid not in allowed_ids:
                continue
            if scores[i] <= 0:
                break
            out.append(cid)
            if len(out) >= top_n:
                break
        return out


# ==================== Citation formatting ====================
def format_citation(rank: int, meta: dict) -> str:
    """Label sitasi utk 1 sumber: [Sumber N: PDF - BAB/Klaster - Pasal X]."""
    pdf = meta.get("pdf_source", "?")
    scope = meta.get("klaster_label") or (f"BAB {meta['bab']}" if meta.get("bab") else "")
    pasal = meta.get("pasal", "?")
    scope_part = f" - {scope}" if scope else ""
    return f"[Sumber {rank}: {pdf}{scope_part} - Pasal {pasal}]"
