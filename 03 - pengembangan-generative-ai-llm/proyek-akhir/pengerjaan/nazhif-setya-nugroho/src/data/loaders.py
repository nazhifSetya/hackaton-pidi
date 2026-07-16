"""
PGABL - PDF Loader untuk RAG (Tahap 1b + Tahap 3).

Design:
- Default pakai pypdf (fastest, identical output vs pdfplumber untuk 4 PDF ini).
- Fallback pdfplumber tersedia via load_pdf(strategy="pdfplumber").
- Reusable ke domain lain: ganti file di data/raw/, tidak sentuh code.

Verify-first prototype: scripts/01_verify_pdf_loader.py
Hasil: semua 4 PDF (PP_5_2021, PP_35_2021, PP_51_2023, UU_6_2023) pakai pypdf clean.
"""

from __future__ import annotations
from pathlib import Path
from typing import Literal


LoaderStrategy = Literal["pypdf", "pdfplumber"]


def load_pdf_pages(pdf_path: Path, strategy: LoaderStrategy = "pypdf") -> list[str]:
    """
    Load semua halaman PDF menjadi list string per-halaman.

    Args:
        pdf_path: absolute atau relative path ke PDF
        strategy: "pypdf" (default, 2-4x lebih cepat) atau "pdfplumber" (robust untuk edge cases)

    Returns:
        List of strings, satu per halaman. String kosong kalau extract_text gagal.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if strategy == "pypdf":
        return _load_with_pypdf(pdf_path)
    elif strategy == "pdfplumber":
        return _load_with_pdfplumber(pdf_path)
    else:
        raise ValueError(f"Unknown strategy: {strategy}. Use 'pypdf' or 'pdfplumber'.")


def _load_with_pypdf(pdf_path: Path) -> list[str]:
    import pypdf
    pages: list[str] = []
    with open(pdf_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception as e:
                pages.append(f"[pypdf error: {e}]")
    return pages


def _load_with_pdfplumber(pdf_path: Path) -> list[str]:
    import pdfplumber
    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception as e:
                pages.append(f"[pdfplumber error: {e}]")
    return pages
