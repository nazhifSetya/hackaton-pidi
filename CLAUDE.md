# CLAUDE.md — Root Repo Hackaton PIDI 2026 (Otak Bersama Lintas Device)

> **File ini di-load OTOMATIS oleh Claude Code setiap sesi, di device mana pun** (Mac & Victus), selama kamu buka Claude Code di dalam repo ini. Ini "otak bersama" yang bikin kerjaan **NYAMBUNG** antar device.
>
> **Baca [🔄 PROTOKOL SYNC](#-protokol-sync-lintas-device-paling-penting) di bawah setiap awal sesi.** Sumber kebenaran status terkini = [`_meta/STATUS.md`](_meta/STATUS.md).

---

## ❓ KENAPA FILE INI ADA (masalah yang dipecahkan)

Kamu kerja pindah-pindah device: **MacBook Air M1** dan **Victus (Windows)**. Masalahnya:

- **Memory & riwayat sesi Claude Code itu LOKAL per-device** (`~/.claude/...`) — **TIDAK ikut ke-sync** antar komputer. Jadi Claude di Victus nggak tahu apa yang Claude di Mac kerjakan kemarin, dan sebaliknya.
- **Yang benar-benar berpindah antar device cuma repo Git ini** (via GitHub `nazhifSetya/hackaton-pidi`).

**Solusinya:** semua konteks penting ditaruh **DI DALAM repo** (ikut Git), dan tiap sesi ikut **ritual sync** di bawah. Dengan begitu Claude di device mana pun baca konteks yang sama = **nyambung**.

> ⚠️ **Yang TIDAK ikut Git** (lihat `.gitignore`): `.venv/`, model berat (`*.h5`, `*.keras`, `*.pt`, `*.safetensors`, dst), `node_modules/`, `saved_model/`, dataset besar. Artefak berat ini **hidup di Google Drive / HuggingFace Hub / Colab**, bukan di repo. **Lokasinya WAJIB dicatat di [`_meta/STATUS.md`](_meta/STATUS.md)** supaya device lain tahu ambil dari mana.

---

## 🔄 PROTOKOL SYNC LINTAS DEVICE (PALING PENTING)

Portabel untuk **zsh (Mac)** dan **PowerShell (Windows/Victus)** — pakai perintah `git` murni (satu per baris; jangan `&&` karena PowerShell lama nggak dukung).

### ▶️ AWAL SESI (WAJIB, sebelum kerja apa pun)

```
git pull --rebase --autostash
```

Lalu **baca [`_meta/STATUS.md`](_meta/STATUS.md)** — khususnya bagian **"FOKUS SAAT INI / HANDOFF"** di atas. Itu ngasih tahu: device terakhir yang kerja, proyek yang lagi digarap, langkah berikutnya, dan yang lagi nunggu (blocked).

> Kalau `git pull` bilang ada konflik: berhenti, kabari user, jangan main resolve sendiri.

### ⏹️ AKHIR SESI (WAJIB, saat mau pindah device / berhenti)

1. **Update [`_meta/STATUS.md`](_meta/STATUS.md):** ubah baris proyek yang barusan digarap + isi ulang bagian **"FOKUS SAAT INI / HANDOFF"** (device, tanggal, langkah berikutnya) + update stempel **"Terakhir di-update"** di paling atas.
2. **Update Progress Log** di `CLAUDE.md` proyek yang bersangkutan (kalau ada tahap selesai).
3. Commit + push:

```
git add -A
git commit -m "sync(<course>/<member>): <ringkas apa yang berubah> [device: mac|victus]"
git push
```

> Karena repo ini **publik**, JANGAN commit rahasia (HF_TOKEN, API key, `.env`). Sudah di-`.gitignore`, tapi tetap cek `git status` sebelum commit.

### 🛠️ Helper opsional (biar nggak ketik manual)

Ada `python _meta/sync.py` (jalan sama di Mac & Windows). Lihat [_meta/sync.py](_meta/sync.py):
- `python _meta/sync.py start` → pull --rebase --autostash + tampilkan handoff dari STATUS.md.
- `python _meta/sync.py status` → status Git + ahead/behind + ringkas STATUS.md.
- `python _meta/sync.py end "pesan commit"` → add + commit + push (konfirmasi dulu).

---

## 👤 KONTEKS PROYEK

- **Apa ini:** repo proyek akhir **course Dicoding Hackaton PIDI 2026**. Satu repo memuat kerjaan **4 anggota tim**, dipisah per-nama, per-course.
- **Pola:** tiap anggota kerjain tema **beda** dengan kode yang **sengaja dibedakan** demi aturan **anti-plagiarisme Dicoding**. Jadi jangan menyamakan/menyalin antar folder anggota.
- **Target default:** **penuhi kriteria minimal dulu** demi kecepatan (kejar lulus), kecuali `CLAUDE.md` proyek tertentu menetapkan target lebih tinggi (banyak punya Nazhif target Advanced ⭐⭐⭐⭐⭐).
- **Gaya komunikasi user (WAJIB):** Bahasa Indonesia simpel, step-by-step, jelaskan *kenapa* bukan cuma *apa*, teliti detail, **jangan asumsi — tanya dulu kalau ambigu**.

### 💻 Dua device

| Device | Spek | Peran |
|---|---|---|
| **MacBook Air M1** | 8 GB RAM | Ringan: orkestrasi, edit kode/notebook, baca dokumen, prototyping non-model, packaging. RAM kecil → hindari training berat. |
| **Victus (Windows)** | 24 GB RAM, RTX 3050 **4 GB VRAM** | Berat: training/inference lokal **selama muat di 4 GB VRAM**. Shell = **PowerShell** (`$env:VAR`, bukan `&&`). |

> **Prioritas eksekusi:** utamakan jalan **lokal** dulu. Kalau mentok (VRAM 4 GB kurang, dependency berat), baru **online gratis** (Google Colab T4 16 GB / HuggingFace / dsb). Pola ini sudah terbukti di proyek-proyek Nazhif.

---

## 🗺️ PETA REPO

```
hackaton-pidi/
├── CLAUDE.md                      ← file ini (otak bersama + protokol sync)
├── _meta/
│   ├── STATUS.md                  ← 📊 DASHBOARD STATUS LINTAS DEVICE (sumber kebenaran)
│   ├── sync.py                    ← helper sync opsional (Mac & Windows)
│   ├── Proposal Hackaton PIDI.docx
│   └── ILT_practicioner/ , everest-architecture.*
│
└── NN - <nama-course>/
    └── <sub-proyek>/              ← "proyek-akhir" (atau utk course 01: "klasifikasi-gambar" & "analisis-sentimen")
        ├── artifact/instruksi/    ← 📕 INSTRUKSI ASLI DICODING (rubric, kriteria) — READ-ONLY
        └── pengerjaan/
            └── <nama-anggota>/    ← kerjaan tiap anggota, self-contained
                ├── CLAUDE.md      ← memory + hard rules + PROGRESS LOG proyek itu
                ├── panduan/       ← checklist & peta kerja
                └── submission/    ← deliverable final (yang di-zip ke Dicoding)
```

**9 course:** `01 fundamental-deep-learning` (2 sub: klasifikasi-gambar + analisis-sentimen), `02 fundamental-generative-ai`, `03 pengembangan-generative-ai-llm`, `04 membangun-sistem-machine-learning`, `05 penerapan-machine-learning-google-cloud`, `06 penerapan-ai-aplikasi-web`, `07 penerapan-machine-learning-flutter`, `08 membangun-proyek-machine-learning`, `09 openshop-restful-api`.

**4 anggota:** `nazhif-setya-nugroho`, `fareynaldi-affan`, `dafina`, `bimo-bramantyo`.

---

## 🧠 HIRARKI MEMORY (di mana konteks disimpan)

Claude Code baca CLAUDE.md dari root turun ke folder kerja. Tiga lapis:

1. **`/CLAUDE.md` (ini)** — peta repo + protokol sync + aturan lintas-device. Berlaku di seluruh repo.
2. **`/_meta/STATUS.md`** — status ringkas SEMUA proyek + handoff antar device. **Baca tiap awal sesi.**
3. **`.../pengerjaan/<anggota>/CLAUDE.md`** — memory DETAIL + HARD RULES + PROGRESS LOG per-proyek. **Saat kerja di satu proyek, baca file ini sepenuhnya.** Aturan proyek lain **tidak berlaku** di sini (tiap proyek self-contained; jangan campur pola antar tema).

> **Aturan emas:** kalau menyelesaikan sesuatu → **update PROGRESS LOG proyek + `_meta/STATUS.md`**, lalu commit+push. Status di kepala Claude hilang saat pindah device; status di file yang bertahan.

---

## ⛔ HARD RULES REPO (lintas semua proyek)

1. **Tiap proyek self-contained.** Jangan sentuh/ubah file di luar folder proyek yang lagi dikerjakan (kecuali `_meta/STATUS.md` & root `CLAUDE.md` untuk sync).
2. **Jangan campur aturan antar proyek/tema.** `CLAUDE.md` proyek A tidak berlaku di proyek B.
3. **`artifact/instruksi/` = READ-ONLY.** Itu instruksi asli Dicoding, jangan diubah.
4. **Anti-plagiarisme:** kode antar anggota memang dibedakan — jangan bikin seragam / copy antar folder anggota.
5. **Repo publik → jangan commit rahasia.** Token/API key via env var / `.env` (sudah di-`.gitignore`). Cek `git status` sebelum commit.
6. **Artefak berat (model, dataset, `.venv`) tidak masuk Git.** Simpan di Drive/HF/Colab, catat lokasi + link di `_meta/STATUS.md`.
7. **Sebelum kerja: `git pull`. Sesudah kerja: update STATUS + commit + push.** (Lihat protokol di atas.)

---

**Akhir root CLAUDE.md.** Detail per-proyek ada di `CLAUDE.md` masing-masing folder anggota. Status terkini & handoff device → [`_meta/STATUS.md`](_meta/STATUS.md).
