"""
PGABL Tahap 1b - Full Ingest ke data/processed/pdfs/

Uses src/data/loaders.py, src/data/cleaners.py, src/rag/chunker.py.
Output: data/processed/pdfs/{PDF_NAME}/chunks.json per PDF.

Cara jalankan (dari root proyek):
  python scripts/03_full_ingest.py
"""

from __future__ import annotations
import json
import sys
import time
from pathlib import Path

# Force UTF-8 stdout (Windows fix)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add src to path (biar bisa import tanpa install)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data.loaders import load_pdf_pages
from src.data.cleaners import clean_pages
from src.rag.chunker import chunk_by_pasal

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed" / "pdfs"

PDFS = [
    "PP_5_2021.pdf",
    "PP_35_2021.pdf",
    "PP_51_2023.pdf",
    "UU_6_2023.pdf",
]


def process_one_pdf(pdf_name: str) -> dict:
    pdf_path = DATA_RAW / pdf_name
    if not pdf_path.exists():
        return {"pdf": pdf_name, "error": f"file not found: {pdf_path}"}

    pdf_source = pdf_name.replace(".pdf", "")
    out_dir = DATA_PROCESSED / pdf_source
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{pdf_name}]")

    # Load
    t0 = time.time()
    raw_pages = load_pdf_pages(pdf_path, strategy="pypdf")
    load_sec = time.time() - t0
    print(f"  Loaded {len(raw_pages)} hlm in {load_sec:.1f}s")

    # Clean
    t0 = time.time()
    cleaned_pages = clean_pages(raw_pages)
    clean_sec = time.time() - t0
    cleaned_full = "\n".join(cleaned_pages)
    print(f"  Cleaned in {clean_sec:.1f}s ({len(cleaned_full):,} chars)")

    # Chunk
    t0 = time.time()
    chunks = chunk_by_pasal(cleaned_full, pdf_source, include_bab_metadata=True)
    chunk_sec = time.time() - t0
    print(f"  Chunked in {chunk_sec:.1f}s -> {len(chunks)} chunks")

    # Save chunks.json
    chunks_path = out_dir / "chunks.json"
    chunks_path.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  Saved: {chunks_path}")

    # Stats
    lengths = [c["length"] for c in chunks]
    return {
        "pdf": pdf_name,
        "total_pages": len(raw_pages),
        "total_chunks": len(chunks),
        "avg_chunk_length": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "truncated_chunks": sum(1 for c in chunks if c["truncated"]),
        "load_sec": round(load_sec, 2),
        "clean_sec": round(clean_sec, 2),
        "chunk_sec": round(chunk_sec, 2),
        "output_path": str(chunks_path.relative_to(ROOT)),
    }


def main():
    print(f"Root: {ROOT}")
    print(f"Input: {DATA_RAW}")
    print(f"Output: {DATA_PROCESSED}")
    print(f"\n{'='*60}")
    print(f"Full Ingest - {len(PDFS)} PDF")
    print(f"{'='*60}")

    all_stats = []
    total_start = time.time()
    for pdf_name in PDFS:
        stats = process_one_pdf(pdf_name)
        all_stats.append(stats)
    total_sec = time.time() - total_start

    # Save summary
    summary_path = DATA_PROCESSED / "_ingest_summary.json"
    summary = {
        "pdfs": all_stats,
        "total_seconds": round(total_sec, 2),
        "total_chunks": sum(s.get("total_chunks", 0) for s in all_stats),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Total: {summary['total_chunks']} chunks dari {len(PDFS)} PDF dalam {total_sec:.1f}s")
    print(f"Summary saved: {summary_path.relative_to(ROOT)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
