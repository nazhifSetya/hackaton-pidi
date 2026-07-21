# CLAUDE.md — 05 Asclepius GCP (Dafina)

> Memory + hard rules + progress log proyek ini. Baca penuh saat kerja di sini. Status lintas device: [`_meta/STATUS.md`](../../../../_meta/STATUS.md).

## Apa ini
Proyek akhir **course 05 — Penerapan Machine Learning dengan Google Cloud** (Dicoding MLGC). Bukan proyek training model — ini **backend/cloud engineering**: web server yang melayani inferensi model deteksi kanker kulit "Asclepius" (Cancer / Non-cancer), lalu deploy ke Google Cloud.

**Target:** Basic (lulus) dulu — tapi karena pakai **Cloud Run**, otomatis kena 2 saran (Kriteria 3 deploy + 7 static IP), plus bisa tambah endpoint `/predict/histories` buat naik bintang.

## ⚠️ Asal-usul folder (PENTING)
Folder ini **hasil `git mv` dari `nazhif-setya-nugroho`** (2026-07-21). Course 05 **dipindah dari Nazhif ke Dafina** (Nazhif tidak jadi ambil course 05). Karena ini **pindah, bukan copy**, dan **Nazhif tidak pernah submit course 05 ke Dicoding**, maka:
- Tidak ada duplikasi kode antar-anggota → **anti-plagiarisme aman tanpa rewrite backend**.
- Yang diganti cuma **string identitas** (project ID / bucket / akun) → Dafina.

## Kondisi kode (dari era Nazhif — TETAP DIPAKAI)
- Backend = **Hapi** + `@tensorflow/tfjs` (pure JS, bukan tfjs-node) + `sharp`. Deploy target **Cloud Run**.
- ✅ **Kode selesai & terverifikasi lokal**: 4 skenario Postman wajib lolos — Cancer→201, Non-cancer→201, >1MB→413, bad-request(grayscale)→400.
- Logika kunci: `inferenceService.js` tolak gambar non-3-channel (biar bad-request.jpg grayscale → 400); score sigmoid >0.5 = Cancer.
- Firestore via `@google-cloud/firestore`, collection `predictions`, doc id = response id.

## HARD RULES
1. Frontend, model kanker, dan kontrak API **dikunci Dicoding** — jangan ubah kontrak response (struktur JSON persis di kriteria).
2. Frontend HANYA edit `src/scripts/api.js` (BASE_URL). Kode lain frontend dari Dicoding, jangan diganti.
3. Identitas GCP harus **Dafina**: project `submissionmlgc-dafina1907`, bucket `-model`, requirements.json isi URL Dafina.
4. Repo publik → jangan commit kredensial GCP / service-account key.

## SISA KERJA (Fase B — butuh Dafina, billing tim yang sama)
Terblokir di deploy GCP. Urutan lengkap ada di [`DEPLOY-NOTES.md`](DEPLOY-NOTES.md). Ringkas:
1. Buat project `submissionmlgc-dafina1907` di **billing account yang sama** (project baru, atas nama Dafina).
2. Download aset (git-ignored): frontend `github.com/dicodingacademy/asclepius`, model TF.js + data-test dari release Dicoding.
3. `gcloud`: enable API → bucket + upload model (public-read) → Firestore native `(default)` → **Cloud Run** deploy backend → set BASE_URL frontend → App Engine deploy.
4. Grant `reviewer_googlecloud@dicoding.com` (Viewer; least-privilege = saran poin).
5. Tes Postman folder "Asclepius Mandatory" (semua hijau) → isi `requirements.json` (4 URL) → ZIP (jangan zip-in-zip) → submit.

## PROGRESS LOG
- **2026-07-21** — Migrasi Nazhif→Dafina (`git mv`), ganti identitas di DEPLOY-NOTES (project/bucket/akun), bikin CLAUDE.md ini, update STATUS. Backend tetap (terverifikasi lokal era Nazhif). **Sisa: Fase B deploy GCP.**
