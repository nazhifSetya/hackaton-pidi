"""
PGABL Tahap 1b - Verify Cleaner + Chunker (VERIFY-FIRST)

Tujuan:
  Test cleaner regex (OCR normalisasi, header/footer strip) + chunker per-pasal
  di 4 PDF. Log hasil ke outputs/samples/ untuk inspection.

Output:
  outputs/samples/chunker_probe.json      - stats per PDF
  outputs/samples/chunker_probe.txt       - human-readable log
  outputs/samples/chunks_sample/          - sample chunks per PDF (first 3 + random 2)
  outputs/samples/cleaner_diff/           - before/after cleaner untuk 1 halaman per PDF

Cara jalankan (dari root proyek):
  python scripts/02_verify_chunker.py
"""

from __future__ import annotations
import json
import re
import sys
import time
from pathlib import Path

# Force UTF-8 stdout (Windows cp1252 fix)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ==================== Paths ====================
ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "outputs" / "samples"
CHUNKS_SAMPLE = OUT_DIR / "chunks_sample"
CLEANER_DIFF = OUT_DIR / "cleaner_diff"
CHUNKS_SAMPLE.mkdir(parents=True, exist_ok=True)
CLEANER_DIFF.mkdir(parents=True, exist_ok=True)

PDFS = ["PP_5_2021.pdf", "PP_35_2021.pdf", "PP_51_2023.pdf", "UU_6_2023.pdf"]


# ==================== Loader ====================
def load_pdf_full(pdf_path: Path) -> list[str]:
    """Load semua halaman via pypdf (fastest, identical output vs pdfplumber)."""
    import pypdf
    pages: list[str] = []
    with open(pdf_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception as e:
                pages.append(f"[loader error: {e}]")
    return pages


# ==================== Cleaner ====================

# Header/footer patterns - repeat tiap halaman, harus di-strip
HEADER_PATTERNS = [
    # PRESIDEN\nREPUBLIK INDONESIA (dan variant garbled)
    r"PRESIDEN\s*\n\s*(?:REPUBLIK|NEPUBUK|REPUBLTI\(?|REPUBLTK|REPTIBLIK)\s*INDONESIA\s*\n",
    # LEMBARAN NEGARA / TAMBAHAN LEMBARAN NEGARA header (di halaman awal saja)
    r"LEMBARAN\s+NEGARA\s*\n\s*REPUBLIK\s+INDONESIA\s*\n",
    # SALINAN header (tepat sebelum PRESIDEN)
    r"^\s*SALINAN\s*\n",
]

FOOTER_PATTERNS = [
    # Page number "-N-" atau "-N -"
    r"\n\s*-\s*\d+\s*-\s*\n",
    r"\n\s*-\s*\d+\s*-\s*$",
    # SK No XXXXX A footer
    r"SK\s+No\s*[\d\s]+\s*[A-Z]?\s*\n?",
]


def normalize_ocr(text: str) -> str:
    """Fix OCR artefak yang common di dokumen legal Indonesia."""
    # 1. Digit O di dalam angka (2O21 → 2021, tapi bukan "Orang")
    text = re.sub(r"(\d)O(\d)", r"\g<1>0\g<2>", text)
    text = re.sub(r"(\d)O$", r"\g<1>0", text, flags=re.MULTILINE)
    # 2. Digit l di dalam angka (l945 → 1945)
    text = re.sub(r"(\d)l(\d)", r"\g<1>1\g<2>", text)
    text = re.sub(r"\bl(\d{3,4})\b", r"1\g<1>", text)  # l945 → 1945 (year context)
    # 3. Common misspellings di garbled OCR
    replacements = {
        r"\bNEPUBUK\b": "REPUBLIK",
        r"\bREPUBLTI\(?\b": "REPUBLIK",
        r"\bREPUBLTK\b": "REPUBLIK",
        r"\bREPTIBLIK\b": "REPUBLIK",
        r"\blndonesia\b": "Indonesia",  # huruf l bukan I
        r"\bkemanusraan\b": "kemanusiaan",
    }
    for pat, repl in replacements.items():
        text = re.sub(pat, repl, text)
    return text


def strip_headers_footers(text: str) -> str:
    """Buang repeated header/footer patterns."""
    for pat in HEADER_PATTERNS:
        text = re.sub(pat, "", text, flags=re.MULTILINE | re.IGNORECASE)
    for pat in FOOTER_PATTERNS:
        text = re.sub(pat, "\n", text, flags=re.MULTILINE)
    return text


def reconstruct_hyphenated_words(pages: list[str]) -> list[str]:
    """
    Gabungkan kata yang terpotong antar halaman (mis. 'keman-\nusraan' → 'kemanusiaan').
    Return list pages baru.
    """
    result = list(pages)
    for i in range(len(result) - 1):
        current = result[i].rstrip()
        # Kalau halaman berakhir dengan word-hyphen
        m = re.search(r"(\w+)-\s*$", current)
        if m:
            trailing = m.group(1)
            next_page = result[i + 1].lstrip()
            n = re.match(r"(\w+)(.*)", next_page, re.DOTALL)
            if n:
                first_word = n.group(1)
                rest = n.group(2)
                # Merge: hapus hyphen di current, prepend joined word ke next page
                result[i] = current[: -(len(trailing) + 1)] + trailing + first_word
                result[i + 1] = rest
    return result


def clean_pages(pages: list[str]) -> list[str]:
    """Full cleaning pipeline per halaman."""
    # 1. Reconstruct hyphenated words across pages BEFORE strip footers
    pages = reconstruct_hyphenated_words(pages)
    # 2. Per-halaman: strip headers/footers + OCR normalize
    cleaned = []
    for p in pages:
        p = strip_headers_footers(p)
        p = normalize_ocr(p)
        cleaned.append(p)
    return cleaned


# ==================== Chunker ====================

# Pasal detection - toleran ke variasi spasi & format
PASAL_REGEX = re.compile(
    r"^\s*Pasal\s+(\d+)\s*$",  # baris tersendiri "Pasal N"
    re.MULTILINE | re.IGNORECASE,
)

# BAB detection - Roman numeral
BAB_REGEX = re.compile(
    r"^\s*BAB\s+([IVXLCDM]+|\d+)\s*(?:$|\n)",
    re.MULTILINE,
)

# "Cukup jelas" di Penjelasan (low-signal, skip di chunking)
CUKUP_JELAS_REGEX = re.compile(
    r"Pasal\s+\d+\s*\n\s*Cukup\s+jelas\s*\.?\s*(\n|$)",
    re.IGNORECASE,
)


def find_pasal_boundaries(full_text: str) -> list[tuple[int, str]]:
    """Return list of (start_offset, pasal_number)."""
    return [(m.start(), m.group(1)) for m in PASAL_REGEX.finditer(full_text)]


def find_bab_boundaries(full_text: str) -> list[tuple[int, str]]:
    return [(m.start(), m.group(1)) for m in BAB_REGEX.finditer(full_text)]


def which_bab_for_offset(offset: int, bab_boundaries: list[tuple[int, str]]) -> str | None:
    """Return BAB yang mencakup offset ini."""
    current = None
    for pos, bab in bab_boundaries:
        if pos <= offset:
            current = bab
        else:
            break
    return current


def chunk_by_pasal(
    full_text: str,
    pdf_name: str,
    include_bab_metadata: bool = True,
    max_chunk_char: int = 5000,
) -> list[dict]:
    """
    Flat chunker per-pasal.
    Kalau include_bab_metadata=True, tambah field 'bab' di setiap chunk.
    """
    pasal_boundaries = find_pasal_boundaries(full_text)
    bab_boundaries = find_bab_boundaries(full_text) if include_bab_metadata else []

    chunks = []
    for i, (start, pasal_num) in enumerate(pasal_boundaries):
        end = pasal_boundaries[i + 1][0] if i + 1 < len(pasal_boundaries) else len(full_text)
        text = full_text[start:end].strip()
        # Skip "Cukup jelas" pasal (low-signal, dari section Penjelasan)
        if CUKUP_JELAS_REGEX.search(text) and len(text) < 100:
            continue
        chunk = {
            "chunk_id": f"{pdf_name.replace('.pdf', '')}_pasal_{pasal_num}_{i}",
            "pdf_source": pdf_name.replace(".pdf", ""),
            "pasal": pasal_num,
            "text": text[:max_chunk_char],
            "length": len(text),
            "truncated": len(text) > max_chunk_char,
        }
        if include_bab_metadata:
            chunk["bab"] = which_bab_for_offset(start, bab_boundaries)
        chunks.append(chunk)
    return chunks


# ==================== Main ====================
def main():
    print(f"Root: {ROOT}")
    print(f"Output: {OUT_DIR}\n")

    all_results = []
    for pdf_name in PDFS:
        print(f"\n{'='*60}")
        print(f"Processing {pdf_name}")
        print(f"{'='*60}")

        pdf_path = DATA_RAW / pdf_name
        if not pdf_path.exists():
            print(f"  SKIP - file not found: {pdf_path}")
            continue

        # === Load ===
        t0 = time.time()
        raw_pages = load_pdf_full(pdf_path)
        elapsed_load = time.time() - t0
        raw_full = "\n".join(raw_pages)
        print(f"  Loaded {len(raw_pages)} hlm in {elapsed_load:.1f}s")
        print(f"  Raw total chars: {len(raw_full):,}")

        # === Clean ===
        t0 = time.time()
        cleaned_pages = clean_pages(raw_pages)
        elapsed_clean = time.time() - t0
        cleaned_full = "\n".join(cleaned_pages)
        print(f"  Cleaned in {elapsed_clean:.1f}s")
        print(f"  Cleaned total chars: {len(cleaned_full):,} "
              f"(delta: {len(cleaned_full) - len(raw_full):+,})")

        # === Save diff for hlm 3 ===
        page_idx_for_diff = 2 if len(raw_pages) > 2 else 0
        diff_content = (
            f"=== BEFORE cleaner (hlm {page_idx_for_diff + 1}, first 1500 char) ===\n"
            + raw_pages[page_idx_for_diff][:1500]
            + "\n\n=== AFTER cleaner (hlm same, first 1500 char) ===\n"
            + cleaned_pages[page_idx_for_diff][:1500]
        )
        (CLEANER_DIFF / f"{pdf_name}__page_{page_idx_for_diff+1}.txt").write_text(
            diff_content, encoding="utf-8"
        )

        # === Chunk ===
        t0 = time.time()
        chunks = chunk_by_pasal(cleaned_full, pdf_name, include_bab_metadata=True)
        elapsed_chunk = time.time() - t0
        print(f"  Chunked in {elapsed_chunk:.1f}s")
        print(f"  Total chunks (pasal-level): {len(chunks)}")

        if chunks:
            lengths = [c["length"] for c in chunks]
            print(f"  Chunk length: min={min(lengths)}, max={max(lengths)}, "
                  f"avg={sum(lengths)/len(lengths):.0f}")

            # BAB coverage
            babs = sorted(set(c["bab"] for c in chunks if c["bab"]))
            print(f"  BAB detected: {len(babs)} - {babs[:10]}{'...' if len(babs)>10 else ''}")

            # Pasal number range
            pasal_nums = [int(c["pasal"]) for c in chunks]
            print(f"  Pasal range: {min(pasal_nums)} - {max(pasal_nums)}")

            # Truncated chunks
            truncated = sum(1 for c in chunks if c["truncated"])
            if truncated > 0:
                print(f"  WARNING: {truncated} chunks > 5000 char (truncated)")

            # === Save sample chunks: first 3 + random 2 ===
            import random
            random.seed(42)
            sample_indices = list(range(min(3, len(chunks))))
            if len(chunks) > 5:
                sample_indices += random.sample(range(3, len(chunks)), 2)
            for idx in sample_indices:
                c = chunks[idx]
                fname = f"{pdf_name}__chunk_{idx:03d}_pasal_{c['pasal']}.txt"
                content = (
                    f"=== chunk_id: {c['chunk_id']} ===\n"
                    f"pdf_source: {c['pdf_source']}\n"
                    f"bab: {c['bab']}\n"
                    f"pasal: {c['pasal']}\n"
                    f"length: {c['length']}\n"
                    f"truncated: {c['truncated']}\n"
                    f"\n--- text ---\n{c['text']}\n"
                )
                (CHUNKS_SAMPLE / fname).write_text(content, encoding="utf-8")

        # === Save summary ===
        result = {
            "pdf": pdf_name,
            "total_pages": len(raw_pages),
            "raw_chars": len(raw_full),
            "cleaned_chars": len(cleaned_full),
            "load_sec": round(elapsed_load, 2),
            "clean_sec": round(elapsed_clean, 2),
            "chunk_sec": round(elapsed_chunk, 2),
            "total_chunks": len(chunks),
        }
        if chunks:
            result["chunk_stats"] = {
                "min_length": min(lengths),
                "max_length": max(lengths),
                "avg_length": round(sum(lengths) / len(lengths), 1),
                "truncated_count": truncated,
                "bab_count": len(babs),
                "bab_detected": babs,
                "pasal_min": min(pasal_nums),
                "pasal_max": max(pasal_nums),
            }
        all_results.append(result)

    # === Save aggregate JSON ===
    json_path = OUT_DIR / "chunker_probe.json"
    json_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")

    # === Save human-readable log ===
    lines = ["=" * 70, "PGABL Tahap 1b - Cleaner + Chunker Probe Log", "=" * 70]
    for r in all_results:
        lines.append(f"\n{r['pdf']}  ({r['total_pages']} hlm)")
        lines.append(f"  Raw chars:     {r['raw_chars']:,}")
        lines.append(f"  Cleaned chars: {r['cleaned_chars']:,} (delta {r['cleaned_chars']-r['raw_chars']:+,})")
        lines.append(f"  Timing: load {r['load_sec']}s + clean {r['clean_sec']}s + chunk {r['chunk_sec']}s")
        lines.append(f"  Total chunks: {r['total_chunks']}")
        if "chunk_stats" in r:
            cs = r["chunk_stats"]
            lines.append(f"  Chunk length: min={cs['min_length']}, max={cs['max_length']}, avg={cs['avg_length']}")
            lines.append(f"  Truncated (>5000 char): {cs['truncated_count']}")
            lines.append(f"  BAB detected ({cs['bab_count']}): {cs['bab_detected']}")
            lines.append(f"  Pasal range: {cs['pasal_min']} - {cs['pasal_max']}")
    log_path = OUT_DIR / "chunker_probe.txt"
    log_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Saved: {json_path}")
    print(f"Saved: {log_path}")
    print(f"Chunk samples: {CHUNKS_SAMPLE}/")
    print(f"Cleaner diffs: {CLEANER_DIFF}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
