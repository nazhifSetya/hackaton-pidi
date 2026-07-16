"""
PGABL Tahap 1b - Verify PDF Loader (VERIFY-FIRST)

Tujuan:
  Probe 4 PDF regulasi untuk decide loader strategy per PDF.
  Test pypdf + pdfplumber di sample halaman, log statistik ke outputs/samples/.

Output:
  outputs/samples/pdf_loader_probe.json  - stats per PDF (page count, text quality)
  outputs/samples/pdf_loader_probe.txt   - human-readable log
  outputs/samples/pdf_first_pages/       - text extract halaman awal per PDF+loader

Cara jalankan (dari root proyek):
  python scripts/01_verify_pdf_loader.py
"""

from __future__ import annotations
import json
import sys
import time
from pathlib import Path

# Force UTF-8 stdout (Windows default cp1252 tidak bisa print unicode arrow dsb)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ==================== Paths ====================
# Script dijalankan dari root proyek.
ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "outputs" / "samples"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIRST_PAGES_DIR = OUT_DIR / "pdf_first_pages"
FIRST_PAGES_DIR.mkdir(parents=True, exist_ok=True)

# ==================== Config ====================
PDFS = [
    "PP_5_2021.pdf",
    "PP_35_2021.pdf",
    "PP_51_2023.pdf",
    "UU_6_2023.pdf",
]

# Halaman yang di-probe: awal (1-3), tengah (percentile), akhir (last 2).
# Kalau PDF < 10 hlm, probe semua.
PROBE_STRATEGY = {
    "first_n": 3,
    "middle_percentiles": [0.25, 0.50, 0.75],
    "last_n": 2,
}


# ==================== Loader wrappers ====================
def load_with_pypdf(pdf_path: Path) -> tuple[list[str], float]:
    """Load semua halaman via pypdf. Return (list_text_per_page, elapsed_sec)."""
    import pypdf
    t0 = time.time()
    pages_text: list[str] = []
    with open(pdf_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            try:
                pages_text.append(page.extract_text() or "")
            except Exception as e:
                pages_text.append(f"[pypdf error: {e}]")
    return pages_text, time.time() - t0


def load_with_pdfplumber(pdf_path: Path, max_pages: int | None = None) -> tuple[list[str], float]:
    """Load halaman via pdfplumber. Bisa dibatasi max_pages untuk PDF besar."""
    import pdfplumber
    t0 = time.time()
    pages_text: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if max_pages and i >= max_pages:
                break
            try:
                pages_text.append(page.extract_text() or "")
            except Exception as e:
                pages_text.append(f"[pdfplumber error: {e}]")
    return pages_text, time.time() - t0


# ==================== Probe helpers ====================
def compute_page_indices(total_pages: int, strategy: dict) -> list[int]:
    """Return sorted unique list of page indices to probe (0-indexed)."""
    if total_pages <= 10:
        return list(range(total_pages))
    indices = set()
    # first N
    for i in range(min(strategy["first_n"], total_pages)):
        indices.add(i)
    # middle percentiles
    for p in strategy["middle_percentiles"]:
        idx = int(total_pages * p)
        indices.add(min(idx, total_pages - 1))
    # last N
    for i in range(max(0, total_pages - strategy["last_n"]), total_pages):
        indices.add(i)
    return sorted(indices)


def text_stats(pages_text: list[str], probe_indices: list[int]) -> dict:
    """Compute statistics untuk pages di probe_indices."""
    lengths = [len(pages_text[i]) for i in probe_indices if i < len(pages_text)]
    if not lengths:
        return {"error": "no pages"}
    return {
        "probed_page_count": len(lengths),
        "chars_min": min(lengths),
        "chars_max": max(lengths),
        "chars_avg": round(sum(lengths) / len(lengths), 1),
        "empty_pages": sum(1 for l in lengths if l == 0),
        "empty_page_ratio": round(sum(1 for l in lengths if l == 0) / len(lengths), 3),
    }


def probe_pdf(pdf_name: str) -> dict:
    """Probe single PDF dgn 2 loader, kumpulkan stats."""
    pdf_path = DATA_RAW / pdf_name
    if not pdf_path.exists():
        return {"pdf": pdf_name, "error": f"file not found: {pdf_path}"}

    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    result: dict = {
        "pdf": pdf_name,
        "size_mb": round(size_mb, 2),
    }

    # --- Try pypdf (semua halaman, fast) ---
    print(f"\n[{pdf_name}] Loading with pypdf...")
    try:
        pages_pypdf, elapsed_pypdf = load_with_pypdf(pdf_path)
        total_pages = len(pages_pypdf)
        probe_idx = compute_page_indices(total_pages, PROBE_STRATEGY)
        stats_pypdf = text_stats(pages_pypdf, probe_idx)
        stats_pypdf["elapsed_sec_total_load"] = round(elapsed_pypdf, 2)
        result["pypdf"] = stats_pypdf
        result["total_pages"] = total_pages
        result["probed_page_indices"] = probe_idx
        # Simpan hlm pertama untuk inspect visual
        for i in probe_idx[:3]:  # first 3 probes
            if i < len(pages_pypdf):
                fname = f"{pdf_name}__pypdf__page_{i+1:04d}.txt"
                (FIRST_PAGES_DIR / fname).write_text(
                    pages_pypdf[i][:3000], encoding="utf-8"
                )
        print(f"  pypdf OK - {total_pages} hlm, {elapsed_pypdf:.1f}s")
    except Exception as e:
        result["pypdf"] = {"error": str(e)}
        print(f"  pypdf FAIL: {e}")
        return result

    # --- Try pdfplumber (kalau file besar, sampling saja untuk hemat waktu) ---
    print(f"[{pdf_name}] Loading with pdfplumber...")
    max_pages_for_pdfplumber = None
    if size_mb > 30 or total_pages > 200:
        # PDF sangat besar (UU 6/2023) - sampling saja, jangan load full 1127 hlm
        max_pages_for_pdfplumber = 100
        print(f"  [SKIP FULL LOAD - PDF besar {size_mb:.0f}MB / {total_pages}hlm - sample first {max_pages_for_pdfplumber} hlm]")

    try:
        pages_plumber, elapsed_plumber = load_with_pdfplumber(
            pdf_path, max_pages=max_pages_for_pdfplumber
        )
        loaded_count = len(pages_plumber)
        probe_idx_plumber = [i for i in probe_idx if i < loaded_count]
        stats_plumber = text_stats(pages_plumber, probe_idx_plumber)
        stats_plumber["elapsed_sec_partial_load"] = round(elapsed_plumber, 2)
        stats_plumber["loaded_pages"] = loaded_count
        stats_plumber["is_partial"] = max_pages_for_pdfplumber is not None
        result["pdfplumber"] = stats_plumber
        # Simpan hlm pertama untuk inspect visual
        for i in probe_idx_plumber[:3]:
            if i < len(pages_plumber):
                fname = f"{pdf_name}__pdfplumber__page_{i+1:04d}.txt"
                (FIRST_PAGES_DIR / fname).write_text(
                    pages_plumber[i][:3000], encoding="utf-8"
                )
        print(f"  pdfplumber OK - loaded {loaded_count} hlm, {elapsed_plumber:.1f}s")
    except Exception as e:
        result["pdfplumber"] = {"error": str(e)}
        print(f"  pdfplumber FAIL: {e}")

    return result


# ==================== Recommendation logic ====================
def recommend_loader(probe_result: dict) -> str:
    """Berdasarkan stats, kasih rekomendasi loader per PDF."""
    if "error" in probe_result:
        return f"SKIP (file error: {probe_result['error']})"

    pypdf_stats = probe_result.get("pypdf", {})
    plumber_stats = probe_result.get("pdfplumber", {})

    # Priority: kalau pypdf clean (avg > 500 char, empty ratio < 0.1) → pypdf
    if pypdf_stats.get("chars_avg", 0) > 500 and pypdf_stats.get("empty_page_ratio", 1) < 0.1:
        return "pypdf (fast, text-layer clean)"

    # Kalau pypdf empty ratio tinggi tapi pdfplumber lebih baik → pdfplumber
    if plumber_stats.get("chars_avg", 0) > pypdf_stats.get("chars_avg", 0) * 1.2:
        return "pdfplumber (better OCR handling)"

    # Kalau size besar → pdfplumber page-by-page (bukan load full)
    if probe_result.get("size_mb", 0) > 30:
        return "pdfplumber page-by-page (batch mode, avoid RAM explode)"

    # Default: pdfplumber
    return "pdfplumber (default, robust for mixed OCR)"


# ==================== Main ====================
def main():
    print(f"Root: {ROOT}")
    print(f"data/raw: {DATA_RAW}")
    print(f"output: {OUT_DIR}")
    print(f"\n{'='*60}")
    print(f"Probe {len(PDFS)} PDF")
    print(f"{'='*60}")

    all_results = []
    for pdf_name in PDFS:
        result = probe_pdf(pdf_name)
        result["recommended_loader"] = recommend_loader(result)
        all_results.append(result)
        print(f"  → Recommendation: {result['recommended_loader']}")

    # ==================== Save JSON ====================
    json_path = OUT_DIR / "pdf_loader_probe.json"
    json_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")

    # ==================== Save human-readable log ====================
    log_lines = []
    log_lines.append("=" * 70)
    log_lines.append("PGABL Tahap 1b - PDF Loader Probe Log")
    log_lines.append("=" * 70)
    for r in all_results:
        log_lines.append(f"\n{r['pdf']}  ({r.get('size_mb', '?')} MB, {r.get('total_pages', '?')} hlm)")
        log_lines.append(f"  Probed page indices: {r.get('probed_page_indices', [])}")
        if "pypdf" in r:
            pp = r["pypdf"]
            if "error" in pp:
                log_lines.append(f"  pypdf: ERROR {pp['error']}")
            else:
                log_lines.append(
                    f"  pypdf:      chars avg={pp['chars_avg']:>7} "
                    f"(min={pp['chars_min']}, max={pp['chars_max']}), "
                    f"empty_pages={pp['empty_pages']}/{pp['probed_page_count']} "
                    f"({pp['empty_page_ratio']*100:.1f}%), "
                    f"load {pp['elapsed_sec_total_load']}s"
                )
        if "pdfplumber" in r:
            pl = r["pdfplumber"]
            if "error" in pl:
                log_lines.append(f"  pdfplumber: ERROR {pl['error']}")
            else:
                partial_note = f" [SAMPLED first {pl['loaded_pages']} hlm]" if pl.get("is_partial") else ""
                log_lines.append(
                    f"  pdfplumber: chars avg={pl['chars_avg']:>7} "
                    f"(min={pl['chars_min']}, max={pl['chars_max']}), "
                    f"empty_pages={pl['empty_pages']}/{pl['probed_page_count']} "
                    f"({pl['empty_page_ratio']*100:.1f}%), "
                    f"load {pl['elapsed_sec_partial_load']}s{partial_note}"
                )
        log_lines.append(f"  → RECOMMEND: {r['recommended_loader']}")

    log_path = OUT_DIR / "pdf_loader_probe.txt"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Saved: {json_path}")
    print(f"Saved: {log_path}")
    print(f"Sample first pages: {FIRST_PAGES_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
