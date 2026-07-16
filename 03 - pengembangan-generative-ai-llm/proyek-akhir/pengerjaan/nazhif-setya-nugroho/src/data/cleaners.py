"""
PGABL - Text Cleaner untuk PDF Legal Indonesia (Tahap 1b).

Kegunaan: strip repeated header/footer + normalize OCR artefak yang common
di dokumen regulasi Indonesia (PP, UU).

Design:
- Config regex di atas (HEADER_PATTERNS, FOOTER_PATTERNS, OCR_REPLACEMENTS).
- Ganti pattern untuk domain lain via extend config, jangan ubah logic.

Verify-first prototype: scripts/02_verify_chunker.py
Hasil: 4 PDF dgn cleanup delta -37 (PP_5_2021), -2052 (PP_35_2021),
       -590 (PP_51_2023), -23,746 (UU_6_2023).
"""

from __future__ import annotations
import re


# ==================== Header patterns (repeat tiap halaman) ====================
HEADER_PATTERNS = [
    # PRESIDEN\nREPUBLIK INDONESIA (dan variant garbled: NEPUBUK, REPUBLTI(, REPUELIK, dst)
    r"PRESIDEN\s*\n\s*(?:REPUBLIK|NEPUBUK|REPUBLTI\(?|REPUBLTK|REPTIBLIK|REPUELIK)\s*INDONESIA\s*\n",
    # LEMBARAN NEGARA header (cover page only)
    r"LEMBARAN\s+NEGARA\s*\n\s*REPUBLIK\s+INDONESIA\s*\n",
    # SALINAN header (tepat sebelum PRESIDEN)
    r"^\s*SALINAN\s*\n",
]


# ==================== Footer patterns ====================
FOOTER_PATTERNS = [
    # Page number "-N-" (dgn spasi/tanpa)
    r"\n\s*-\s*\d+\s*-\s*\n",
    r"\n\s*-\s*\d+\s*-\s*$",
    # SK No XXXXX A footer (tapi bukan SK dalam text lain)
    r"SK\s+No\s*[\d\s]+\s*[A-Z]?\s*(?:\n|$)",
]


# ==================== OCR replacements ====================
# Format: {regex_pattern: replacement}
OCR_REPLACEMENTS = {
    # Garbled REPUBLIK variants
    r"\bNEPUBUK\b": "REPUBLIK",
    r"\bREPUBLTI\(?\b": "REPUBLIK",
    r"\bREPUBLTK\b": "REPUBLIK",
    r"\bREPTIBLIK\b": "REPUBLIK",
    r"\bREPUELIK\b": "REPUBLIK",
    # Lower-case 'l' bukannya 'I'
    r"\blndonesia\b": "Indonesia",
    r"\blndo\b": "Indo",
    # Common misspellings from OCR
    r"\bkemanusraan\b": "kemanusiaan",
    r"\bpersekutrran\b": "persekutuan",
}


def normalize_ocr(text: str) -> str:
    """Fix OCR artefak yang common di dokumen legal Indonesia."""
    # Digit O di dalam angka (2O21 -> 2021), tapi bukan huruf O di kata biasa
    text = re.sub(r"(\d)O(\d)", r"\g<1>0\g<2>", text)
    text = re.sub(r"(\d)O$", r"\g<1>0", text, flags=re.MULTILINE)
    # Digit l di dalam angka (l945 -> 1945)
    text = re.sub(r"(\d)l(\d)", r"\g<1>1\g<2>", text)
    text = re.sub(r"\bl(\d{3,4})\b", r"1\g<1>", text)
    # Word-level replacements
    for pattern, repl in OCR_REPLACEMENTS.items():
        text = re.sub(pattern, repl, text)
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
    Gabungkan kata yang terpotong antar halaman (mis. 'keman-\nusraan' -> 'kemanusiaan').
    In-place modification, tapi return new list.
    """
    result = list(pages)
    for i in range(len(result) - 1):
        current = result[i].rstrip()
        m = re.search(r"(\w+)-\s*$", current)
        if m:
            trailing = m.group(1)
            next_page = result[i + 1].lstrip()
            n = re.match(r"(\w+)(.*)", next_page, re.DOTALL)
            if n:
                first_word = n.group(1)
                rest = n.group(2)
                result[i] = current[: -(len(trailing) + 1)] + trailing + first_word
                result[i + 1] = rest
    return result


def clean_pages(pages: list[str]) -> list[str]:
    """
    Full pipeline: reconstruct hyphenated -> strip headers/footers -> normalize OCR.

    Return: list halaman baru dgn text bersih.
    """
    pages = reconstruct_hyphenated_words(pages)
    cleaned = []
    for p in pages:
        p = strip_headers_footers(p)
        p = normalize_ocr(p)
        cleaned.append(p)
    return cleaned
