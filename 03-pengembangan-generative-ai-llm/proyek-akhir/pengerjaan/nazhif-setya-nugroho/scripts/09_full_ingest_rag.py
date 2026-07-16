"""
PGABL Tahap 3a - Full Ingest RAG (VERIFY-FIRST lokal).

Pipeline: load 4 PDF (pypdf) -> clean -> chunk (per-pasal + sub-split overlap) ->
  chunks.json per PDF + laporan verifikasi ke outputs/samples/.

UU_6_2023 pakai map_klaster_by_bab=True -> klaster_id 1-15 (= 15 collection).

Cara jalankan (dari root proyek, pakai venv yang punya pypdf+pyyaml):
  <venv>/bin/python scripts/09_full_ingest_rag.py

Verifikasi yang dicek laporan:
  1. Jumlah chunk per PDF + total
  2. Distribusi char_len (max <= chunk_size, kecuali blok tak-terpotong? tidak - sub-split jamin <=chunk_size)
  3. OVERLAP EKSPLISIT terbukti: part[k][-overlap:] == part[k+1][:overlap]
  4. UU: distribusi chunk per klaster_id (1-15) + jumlah bab=None
  5. Sampel chunk (termasuk area lembur PP_35 & UU klaster Ketenagakerjaan)
"""

from __future__ import annotations
import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data.loaders import load_pdf_pages
from src.data.cleaners import clean_pages
from src.rag.chunker import chunk_by_pasal, refine_uu_klaster

# PDF ada di artifacts (read-only). Map nama asli -> pdf_source path-safe.
ARTIFACTS = ROOT / "artifacts" / "document_knowledge_RAG"
PDF_MAP = {
    "PP_5_2021": "PP Nomor 5 Tahun 2021.pdf",
    "PP_35_2021": "PP Nomor 35 Tahun 2021.pdf",
    "PP_51_2023": "PP Nomor 51 Tahun 2023.pdf",
    "UU_6_2023": "UU Nomor 6 Tahun 2023.pdf",
}
# PDF yang di-map klaster per-BAB (hanya UU 6/2023)
KLASTER_PDF = "UU_6_2023"

DATA_PROCESSED = ROOT / "data" / "processed" / "pdfs"
SAMPLES = ROOT / "outputs" / "samples"

CFG = yaml.safe_load((ROOT / "configs" / "rag_config.yaml").read_text(encoding="utf-8"))
FLAT = CFG["chunker"]["flat"]
CHUNK_SIZE = FLAT["chunk_size"]
OVERLAP = FLAT["chunk_overlap"]
HARD_CAP = FLAT["hard_cap"]


def pct(vals, p):
    if not vals:
        return 0
    s = sorted(vals)
    k = int(round((p / 100) * (len(s) - 1)))
    return s[k]


def process_one(pdf_source: str) -> dict:
    pdf_path = ARTIFACTS / PDF_MAP[pdf_source]
    is_klaster = pdf_source == KLASTER_PDF
    out_dir = DATA_PROCESSED / pdf_source
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    raw_pages = load_pdf_pages(pdf_path, strategy="pypdf")
    load_sec = time.time() - t0

    t0 = time.time()
    cleaned = clean_pages(raw_pages)
    full = "\n".join(cleaned)
    clean_sec = time.time() - t0

    t0 = time.time()
    chunks = chunk_by_pasal(
        full,
        pdf_source,
        include_bab_metadata=True,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=OVERLAP,
        hard_cap=HARD_CAP,
        skip_cukup_jelas=True,
        map_klaster_by_bab=is_klaster,
    )
    # UU 6/2023: refine klaster (route Penjelasan ke klaster benar + tag jenis)
    refine_info = None
    if is_klaster:
        refine_info = refine_uu_klaster(chunks, full)
    chunk_sec = time.time() - t0

    (out_dir / "chunks.json").write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    char_lens = [c["char_len"] for c in chunks]
    n_sub = sum(1 for c in chunks if c["is_subchunk"])
    n_whole = len(chunks) - n_sub
    over_cap = sum(1 for c in chunks if c["char_len"] > CHUNK_SIZE)

    # --- Verifikasi overlap eksplisit: cari pasal dgn n_subchunks>1, cek invariant ---
    overlap_checks = []
    by_pasalgroup = defaultdict(list)
    for c in chunks:
        if c["n_subchunks"] > 1:
            key = c["chunk_id"].rsplit("_sub", 1)[0]
            by_pasalgroup[key].append(c)
    for key, group in list(by_pasalgroup.items())[:3]:  # ambil 3 grup sebagai bukti
        group = sorted(group, key=lambda x: x["sub_index"])
        for a, b in zip(group, group[1:]):
            ok = a["text"][-OVERLAP:] == b["text"][:OVERLAP]
            overlap_checks.append({
                "chunk_pair": [a["chunk_id"], b["chunk_id"]],
                "overlap_len_expected": OVERLAP,
                "overlap_matches": ok,
                "tail_of_a": a["text"][-OVERLAP:][:60],
                "head_of_b": b["text"][:OVERLAP][:60],
            })

    stats = {
        "pdf_source": pdf_source,
        "total_pages": len(raw_pages),
        "cleaned_chars": len(full),
        "total_chunks": len(chunks),
        "whole_pasal_chunks": n_whole,
        "subchunks": n_sub,
        "chunks_over_chunk_size": over_cap,  # harus 0 (sub-split jamin <= chunk_size)
        "char_len_min": min(char_lens) if char_lens else 0,
        "char_len_p50": pct(char_lens, 50),
        "char_len_p95": pct(char_lens, 95),
        "char_len_max": max(char_lens) if char_lens else 0,
        "load_sec": round(load_sec, 2),
        "clean_sec": round(clean_sec, 2),
        "chunk_sec": round(chunk_sec, 2),
        "overlap_checks": overlap_checks,
    }

    if is_klaster:
        klaster_dist = Counter(c.get("klaster_id") for c in chunks)
        jenis_dist = Counter(c.get("jenis") for c in chunks)
        bab_none = sum(1 for c in chunks if c["bab"] is None)
        klaster_none = sum(1 for c in chunks if c.get("klaster_id") is None)
        stats["refine_info"] = refine_info
        stats["bab_none_chunks"] = bab_none
        stats["klaster_none_chunks_after_refine"] = klaster_none  # harus 0
        stats["jenis_distribution"] = dict(jenis_dist)
        stats["klaster_distribution"] = {
            str(k): klaster_dist.get(k, 0) for k in list(range(1, 16)) + [None]
        }
        stats["empty_klaster_collections"] = [k for k in range(1, 16) if klaster_dist.get(k, 0) == 0]

    return stats, chunks


def sample_chunks(chunks, predicate, n=2):
    out = []
    for c in chunks:
        if predicate(c):
            out.append({
                "chunk_id": c["chunk_id"],
                "bab": c.get("bab"),
                "klaster_label": c.get("klaster_label"),
                "pasal": c["pasal"],
                "char_len": c["char_len"],
                "text_head": c["text"][:400],
            })
            if len(out) >= n:
                break
    return out


def main():
    SAMPLES.mkdir(parents=True, exist_ok=True)
    print(f"chunk_size={CHUNK_SIZE} overlap={OVERLAP} hard_cap={HARD_CAP}")
    report = {"config": {"chunk_size": CHUNK_SIZE, "overlap": OVERLAP, "hard_cap": HARD_CAP},
              "pdfs": [], "samples": {}}
    all_chunks = {}
    total_start = time.time()
    for src in PDF_MAP:
        print(f"[{src}] ...", flush=True)
        stats, chunks = process_one(src)
        report["pdfs"].append(stats)
        all_chunks[src] = chunks
        print(f"  -> {stats['total_chunks']} chunks "
              f"(whole={stats['whole_pasal_chunks']}, sub={stats['subchunks']}, "
              f"maxlen={stats['char_len_max']})", flush=True)

    report["total_chunks"] = sum(s["total_chunks"] for s in report["pdfs"])
    report["total_seconds"] = round(time.time() - total_start, 2)
    report["n_collections_expected"] = 3 + 15  # 3 PP + 15 klaster UU

    # Sampel penting untuk sanity legal:
    # 1) PP_35 area lembur (pasal upah lembur biasanya di kisaran 78/79 UU asal -> di PP 35 Pasal 31/32)
    report["samples"]["pp35_lembur"] = sample_chunks(
        all_chunks["PP_35_2021"],
        lambda c: "lembur" in c["text"].lower(), n=3)
    # 2) UU klaster 4 (Ketenagakerjaan)
    report["samples"]["uu_klaster4_ketenagakerjaan"] = sample_chunks(
        all_chunks["UU_6_2023"],
        lambda c: c.get("klaster_id") == 4, n=3)
    # 3) UU chunk yang bab=None (kalau ada) - untuk lihat apa isinya
    report["samples"]["uu_bab_none"] = sample_chunks(
        all_chunks["UU_6_2023"],
        lambda c: c["bab"] is None, n=3)
    # 4) Contoh sub-chunk (bukti overlap)
    report["samples"]["subchunk_example"] = sample_chunks(
        all_chunks["UU_6_2023"],
        lambda c: c["is_subchunk"], n=2)
    # 5) BUKTI ROUTING: chunk PENJELASAN yang berhasil masuk klaster_4 (Ketenagakerjaan)
    report["samples"]["penjelasan_routed_to_klaster4"] = sample_chunks(
        all_chunks["UU_6_2023"],
        lambda c: c.get("jenis") == "penjelasan" and c.get("klaster_id") == 4, n=3)
    # 6) BUKTI: chunk PENJELASAN yang tersisa di klaster_15 (harus sedikit, real Ketentuan Penutup)
    report["samples"]["klaster15_remaining"] = sample_chunks(
        all_chunks["UU_6_2023"],
        lambda c: c.get("klaster_id") == 15, n=3)

    (SAMPLES / "rag_chunk_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nTotal {report['total_chunks']} chunks dalam {report['total_seconds']}s")
    print(f"Report: outputs/samples/rag_chunk_report.json")


if __name__ == "__main__":
    main()
