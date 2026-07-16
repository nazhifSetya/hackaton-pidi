"""
PGABL - Chunker untuk Legal PDF (Tahap 1b + Tahap 3).

Strategy per-pasal (flat) untuk semua 4 PDF:
- Regex `^\\s*Pasal\\s+(\\d+)\\s*$` split jadi 1 blok per pasal.
- Blok pasal > chunk_size di-sub-split dgn OVERLAP EKSPLISIT (rubric WAJIB).
- Metadata: bab (Roman numeral), pasal, chunk_id, pdf_source.
- Khusus UU_6_2023: map BAB Roman I-XV -> klaster_id 1-15 + label tema
  (dipakai untuk 15 collection ChromaDB per klaster di Tahap 3).

Verify-first prototype: scripts/09_full_ingest_rag.py -> outputs/samples/.

Reusable ke domain lain: ganti PASAL_REGEX / BAB_REGEX / klaster map via argumen,
logic split tidak berubah.
"""

from __future__ import annotations
import re
from typing import Optional


# Pasal detection - baris tersendiri, toleran spasi
PASAL_REGEX = re.compile(r"^\s*Pasal\s+(\d+)\s*$", re.MULTILINE | re.IGNORECASE)

# BAB detection - Roman numeral standalone
BAB_REGEX = re.compile(r"^\s*BAB\s+([IVXLCDM]+)\s*$", re.MULTILINE)

# "Cukup jelas" di section Penjelasan (low-signal, di-skip)
CUKUP_JELAS_REGEX = re.compile(
    r"Pasal\s+\d+\s*\n\s*Cukup\s+jelas\s*\.?\s*(?:\n|$)",
    re.IGNORECASE,
)


# ==================== UU 6/2023: BAB (Roman) -> Klaster ====================
# UU 6/2023 (Cipta Kerja) punya TEPAT 15 BAB. "15 klaster" di desain = 15 BAB.
# Terverifikasi via recon lokal (semua BAB I-XV terdeteksi bersih).
# Label tema dipakai untuk sitasi sumber yang enak dibaca legal team.
UU_6_2023_KLASTER_LABELS = {
    1: "Ketentuan Umum",
    2: "Asas, Tujuan, dan Ruang Lingkup",
    3: "Peningkatan Ekosistem Investasi dan Kegiatan Berusaha",
    4: "Ketenagakerjaan",
    5: "Koperasi dan UMK-M",
    6: "Kemudahan Berusaha",
    7: "Dukungan Riset dan Inovasi",
    8: "Pengadaan Tanah",
    9: "Kawasan Ekonomi",
    10: "Investasi Pemerintah Pusat dan Proyek Strategis Nasional",
    11: "Administrasi Pemerintahan",
    12: "Pengawasan dan Pembinaan",
    13: "Ketentuan Lain-Lain",
    14: "Ketentuan Peralihan",
    15: "Ketentuan Penutup",
}

_ROMAN_MAP = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


# Keyword routing untuk chunk PENJELASAN (yang tak bisa di-track per-pasal karena didominasi
# referensi UU sektor). Chunk penjelasan diarahkan ke klaster dgn hit keyword terbanyak;
# kalau nol match -> fallback klaster 3 (Ekosistem Investasi = cluster dominan/catch-all).
# Keyword lowercase; dicek substring pada text lowercase.
UU_6_2023_KLASTER_KEYWORDS = {
    4: ["pekerja", "buruh", "pengupahan", "upah minimum", "upah kerja", "lembur",
        "pkwt", "pemutusan hubungan kerja", "pesangon", "tenaga kerja", "serikat pekerja",
        "waktu kerja", "hubungan kerja", "perjanjian kerja", "jaminan sosial",
        "tenaga kerja asing", "pelatihan kerja"],
    5: ["koperasi", "usaha mikro", "usaha kecil", "usaha menengah", "umk-m", "umkm"],
    6: ["perseroan terbatas", "badan hukum", "keimigrasian", "hak kekayaan intelektual",
        "paten", "merek", "perkumpulan"],
    8: ["pengadaan tanah", "ganti kerugian", "pelepasan hak", "bank tanah"],
    9: ["kawasan ekonomi khusus", "kawasan perdagangan bebas", "kawasan ekonomi",
        "zona ekonomi"],
    10: ["proyek strategis nasional", "investasi pemerintah pusat", "lembaga pengelola investasi"],
    7: ["riset dan inovasi", "riset", "inovasi"],
    3: ["perizinan berusaha", "nomor induk berusaha", "sistem oss", "kbli", "berbasis risiko",
        "lingkungan hidup", "bangunan gedung", "tata ruang", "kehutanan", "sumber daya air",
        "kelautan", "perikanan", "ketenaganukliran", "pelayaran", "penerbangan", "pos",
        "telekomunikasi", "energi", "ketenagalistrikan", "perdagangan", "perindustrian"],
}


def route_penjelasan_by_keyword(text: str, fallback_klaster: int = 3) -> int:
    """Klaster untuk 1 chunk penjelasan via hit keyword terbanyak; nol match -> fallback."""
    low = text.lower()
    best_k, best_hits = fallback_klaster, 0
    for kid, kws in UU_6_2023_KLASTER_KEYWORDS.items():
        hits = sum(low.count(kw) for kw in kws)
        if hits > best_hits:
            best_k, best_hits = kid, hits
    return best_k


def roman_to_int(roman: str) -> Optional[int]:
    """Konversi Roman numeral ke int. Return None kalau input invalid."""
    if not roman:
        return None
    roman = roman.upper()
    total, prev = 0, 0
    for ch in reversed(roman):
        if ch not in _ROMAN_MAP:
            return None
        val = _ROMAN_MAP[ch]
        total += -val if val < prev else val
        prev = max(prev, val)
    return total if total > 0 else None


def find_pasal_boundaries(full_text: str) -> list[tuple[int, str]]:
    """Return list of (char_offset, pasal_number)."""
    return [(m.start(), m.group(1)) for m in PASAL_REGEX.finditer(full_text)]


def find_bab_boundaries(full_text: str) -> list[tuple[int, str]]:
    """Return list of (char_offset, bab_id)."""
    return [(m.start(), m.group(1)) for m in BAB_REGEX.finditer(full_text)]


def which_bab_for_offset(offset: int, bab_boundaries: list[tuple[int, str]]) -> Optional[str]:
    """Return BAB yang mencakup offset ini, atau None kalau di luar BAB apapun."""
    current = None
    for pos, bab in bab_boundaries:
        if pos <= offset:
            current = bab
        else:
            break
    return current


def split_text_with_overlap(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Sliding-window split dgn OVERLAP EKSPLISIT (rubric WAJIB, bukan default library).

    Kalau text <= chunk_size -> 1 chunk utuh (tidak dipecah).
    Kalau lebih panjang -> potongan sepanjang chunk_size dgn step (chunk_size - overlap).
    Invariant: part[k][-overlap:] == part[k+1][:overlap] (overlap persis `overlap` char).
    """
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) harus < chunk_size ({chunk_size})")
    if len(text) <= chunk_size:
        return [text]
    parts: list[str] = []
    step = chunk_size - overlap
    start = 0
    while start < len(text):
        parts.append(text[start:start + chunk_size])
        if start + chunk_size >= len(text):
            break
        start += step
    return parts


def chunk_by_pasal(
    full_text: str,
    pdf_source: str,
    include_bab_metadata: bool = True,
    chunk_size: int = 1200,
    chunk_overlap: int = 100,
    hard_cap: int = 5000,
    skip_cukup_jelas: bool = True,
    map_klaster_by_bab: bool = False,
) -> list[dict]:
    """
    Chunker flat per-pasal dgn sub-split overlap eksplisit.

    Args:
        full_text: teks lengkap PDF (setelah cleaner).
        pdf_source: nama PDF tanpa .pdf (mis. "PP_35_2021").
        include_bab_metadata: kalau True, tambah field 'bab' di setiap chunk.
        chunk_size: panjang target chunk (char). Blok pasal > ini di-sub-split.
        chunk_overlap: overlap antar sub-chunk (char). EKSPLISIT (rubric WAJIB).
        hard_cap: batas keras char per chunk (rubric max 5000) - safety net.
        skip_cukup_jelas: skip pasal Penjelasan yang isinya cuma "Cukup jelas".
        map_klaster_by_bab: kalau True (khusus UU_6_2023), tambah klaster_id + klaster_label
                            dari BAB Roman (I->1 .. XV->15).

    Returns:
        List dict, tiap chunk punya:
          - chunk_id: str unik (mis. "PP_35_2021_pasal_1_0" atau "..._0_sub1" utk sub-chunk)
          - pdf_source, pasal, bab (Optional)
          - text: str (isi, di-cap di hard_cap)
          - length: int (panjang blok pasal ORIGINAL, sebelum sub-split)
          - char_len: int (panjang text chunk ini)
          - is_subchunk: bool, sub_index: int, n_subchunks: int
          - (UU only) klaster_id: Optional[int], klaster_label: Optional[str]
    """
    pasal_boundaries = find_pasal_boundaries(full_text)
    bab_boundaries = find_bab_boundaries(full_text) if include_bab_metadata else []

    chunks: list[dict] = []
    for i, (start, pasal_num) in enumerate(pasal_boundaries):
        end = pasal_boundaries[i + 1][0] if i + 1 < len(pasal_boundaries) else len(full_text)
        block = full_text[start:end].strip()

        # Skip "Cukup jelas" pasal (low-signal dari Penjelasan)
        if skip_cukup_jelas and CUKUP_JELAS_REGEX.search(block) and len(block) < 100:
            continue

        bab = which_bab_for_offset(start, bab_boundaries) if include_bab_metadata else None
        klaster_id = None
        klaster_label = None
        if map_klaster_by_bab and bab is not None:
            kid = roman_to_int(bab)
            if kid is not None and kid in UU_6_2023_KLASTER_LABELS:
                klaster_id = kid
                klaster_label = UU_6_2023_KLASTER_LABELS[kid]

        sub_texts = split_text_with_overlap(block, chunk_size, chunk_overlap)
        n_sub = len(sub_texts)
        for j, sub in enumerate(sub_texts):
            chunk_id = (
                f"{pdf_source}_pasal_{pasal_num}_{i}"
                if n_sub == 1
                else f"{pdf_source}_pasal_{pasal_num}_{i}_sub{j}"
            )
            chunk = {
                "chunk_id": chunk_id,
                "pdf_source": pdf_source,
                "pasal": pasal_num,
                "bab": bab,
                "text": sub[:hard_cap],
                "length": len(block),
                "char_len": len(sub[:hard_cap]),
                "char_offset": start,          # offset blok pasal di full_text (utk routing UU)
                "is_subchunk": n_sub > 1,
                "sub_index": j,
                "n_subchunks": n_sub,
            }
            if map_klaster_by_bab:
                chunk["klaster_id"] = klaster_id
                chunk["klaster_label"] = klaster_label
                chunk["jenis"] = "batang_tubuh"   # default; di-refine oleh refine_uu_klaster
            chunks.append(chunk)

    return chunks


# ==================== UU 6/2023: routing Penjelasan -> klaster benar ====================
# Masalah: PENJELASAN besar (pasal-demi-pasal) ada SETELAH BAB XV & tak pakai header BAB,
# jadi kalau naif semua chunk Penjelasan mewarisi bab=XV -> nyasar ke klaster_15.
# Fix: (1) deteksi batas Penjelasan, (2) bangun backbone pasal-Cipta-Kerja (1..186, berurutan)
#      dari batang tubuh -> peta own_pasal->klaster, (3) route tiap chunk Penjelasan via
#      pasal yang dijelaskannya (tracking monotonic; referensi UU sektor = noise, di-skip).

def find_penjelasan_offset(full_text: str) -> int:
    """Offset awal PENJELASAN besar = 'PENJELASAN ATAS' pertama SETELAH BAB terakhir."""
    bab_bounds = find_bab_boundaries(full_text)
    last_bab_off = bab_bounds[-1][0] if bab_bounds else 0
    for m in re.finditer(r"PENJELASAN\s*\n?\s*ATAS", full_text):
        if m.start() > last_bab_off:
            return m.start()
    ms = [m.start() for m in re.finditer(r"\bPENJELASAN\b", full_text)]
    return ms[-1] if ms else len(full_text)


def build_own_pasal_backbone(full_text: str, pen_offset: int) -> list[tuple[int, int]]:
    """
    Peta breakpoint (own_pasal_start, klaster_id) per BAB di batang tubuh.

    Robust: dijangkar ke 15 header BAB (terdeteksi bersih), BUKAN rantai berurutan yang
    rapuh terhadap glitch OCR. Untuk tiap BAB (dedupe first-occurrence, buang stray duplikat),
    ambil 'Pasal N' standalone PERTAMA setelah header BAB itu sebagai own_pasal awal klaster.
    Guard monotonic (num > prev) supaya stray/embedded tidak merusak urutan.

    Return list (own_pasal_start, klaster_id) urut naik own_pasal.
    Contoh: [(1,1),(2,2),(4,3),(80,4),(85,5),...] -> klaster_for_own_pasal binary-lookup.
    """
    matches = list(PASAL_REGEX.finditer(full_text))
    # Dedupe BAB: keep first occurrence per roman (buang stray duplikat spt 'BAB V' kedua)
    seen: set[str] = set()
    ordered_bab: list[tuple[int, str]] = []
    for off, roman in find_bab_boundaries(full_text):
        if off >= pen_offset:
            break
        if roman not in seen:
            seen.add(roman)
            ordered_bab.append((off, roman))

    backbone: list[tuple[int, int]] = []
    prev = -1
    for off, roman in ordered_bab:
        kid = roman_to_int(roman)
        if kid is None:
            continue
        for m in matches:
            if m.start() > off:
                num = int(m.group(1))
                if prev < num <= 250:          # monotonic + plausible
                    backbone.append((num, kid))
                    prev = num
                break
    return backbone


def klaster_for_own_pasal(n: int, backbone: list[tuple[int, int]]) -> Optional[int]:
    """Klaster dari own_pasal terbesar di backbone yang <= n."""
    kid = None
    for own, k in backbone:
        if own <= n:
            kid = k
        else:
            break
    return kid


def refine_uu_klaster(chunks: list[dict], full_text: str) -> dict:
    """
    Refine klaster UU 6/2023 in-place:
      - tandai jenis (batang_tubuh / penjelasan) via offset batas Penjelasan
      - batang tubuh: pakai klaster dari BAB (sudah ada); bab=None -> klaster_1 (front matter)
      - penjelasan: route ke klaster benar via own-pasal yang dijelaskan (tracking monotonic)
    Return ringkasan (offset, ukuran backbone) untuk laporan verifikasi.
    """
    pen_offset = find_penjelasan_offset(full_text)
    backbone = build_own_pasal_backbone(full_text, pen_offset)

    # Batang tubuh: klaster dari BAB (sudah di-set). Penjelasan: keyword routing (per-pasal
    # tidak reliable karena didominasi referensi UU sektor setelah own Pasal ~17).
    n_penjelasan = 0
    for c in chunks:
        off = c.get("char_offset", 0)
        if off >= pen_offset:
            c["jenis"] = "penjelasan"
            k = route_penjelasan_by_keyword(c["text"], fallback_klaster=3)
            c["klaster_id"] = k
            c["klaster_label"] = UU_6_2023_KLASTER_LABELS.get(k)
            n_penjelasan += 1
        else:
            c["jenis"] = "batang_tubuh"
            if c.get("klaster_id") is None:      # bab=None front matter -> Ketentuan Umum
                c["klaster_id"] = 1
                c["klaster_label"] = UU_6_2023_KLASTER_LABELS[1]

    return {
        "penjelasan_offset": pen_offset,
        "penjelasan_offset_pct": round(100 * pen_offset / max(len(full_text), 1), 1),
        "n_penjelasan_chunks": n_penjelasan,
        "penjelasan_routing": "keyword",
        "backbone_size": len(backbone),
        "backbone_own_pasal_max": backbone[-1][0] if backbone else 0,
        "backbone_klaster_transitions": _klaster_transitions(backbone),
    }


def _klaster_transitions(backbone: list[tuple[int, int]]) -> list[dict]:
    """Ringkas backbone jadi rentang own_pasal per klaster (utk verifikasi)."""
    out: list[dict] = []
    for own, k in backbone:
        if out and out[-1]["klaster_id"] == k:
            out[-1]["own_pasal_end"] = own
        else:
            out.append({"klaster_id": k, "own_pasal_start": own, "own_pasal_end": own})
    return out
