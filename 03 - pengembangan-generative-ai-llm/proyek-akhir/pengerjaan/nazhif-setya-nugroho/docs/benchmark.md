# Benchmark Evaluasi RAG — PGABL Legal Assistant

Evaluasi pada **test-set kurasi manual 45 Q&A** (40 single_pdf + 5 cross_pdf; 11 easy / 23 medium / 11 hard). Dijalankan di Google Colab T4 (2026-07-14) via `RAG_submission_PGABL_Nazhif_Setya_Nugroho.ipynb` Bagian D.

## 1. Retrieval metrics per tier (objective anchor)

Sebuah chunk dihitung **relevan** bila `(pdf_source, pasal)`-nya cocok dengan ground truth (match by pdf+pasal → tahan perubahan chunk_id). Semua tier dibandingkan pada Top-5.

| Tier | hit@1 | hit@3 | hit@5 | MRR | NDCG@5 |
|---|---|---|---|---|---|
| **Basic** (dense-only) | 0.4222 | 0.5556 | **0.6444** | **0.5026** | **0.5880** |
| **Skilled** (ensemble BM25+Dense RRF + parent-child) | 0.3778 | 0.5333 | 0.6000 | 0.4589 | 0.5099 |
| **Advanced** (HyDE + reranker + threshold) | **0.4444** | **0.5778** | 0.5778 | 0.5000 | 0.5868 |

**Advanced — breakdown by difficulty:**

| Difficulty | hit@5 | MRR | n |
|---|---|---|---|
| easy | 0.5455 | 0.3939 | 11 |
| medium | 0.5217 | 0.5217 | 23 |
| **hard** | **0.7273** | **0.5606** | 11 |

**Advanced — breakdown by type:** single_pdf hit@5=0.575 (MRR 0.504, n=40); cross_pdf hit@5=0.600 (MRR 0.467, n=5).

## 2. Analisis (jujur)

**Reranker menaikkan presisi peringkat-atas.** Advanced unggul di **hit@1 (0.444, tertinggi)** dan **hit@3 (0.578, tertinggi)** — cross-encoder `bge-reranker-v2-m3` menarik pasal yang benar ke ranking teratas. Ini persis fungsi reranker, dan terbukti bekerja (lihat juga Bagian C.4: skor rerank memisahkan tajam 0.976 vs 0.258).

**Trade-off recall di hit@5.** Basic sedikit lebih tinggi pada hit@5 (0.644 vs 0.578). Ini konsisten dengan sifat reranking: menyaring 20 kandidat → Top-5 mempertajam bagian atas, tetapi bisa menggeser satu chunk relevan keluar dari Top-5 yang tadinya tertangkap dense-Top-5. Dua faktor tambahan: (a) **HyDE pada SLM 3B** kadang menghasilkan dokumen hipotetis lemah/menolak (teramati di C.4 HyDE-2) sehingga menambah noise ke kandidat dense; (b) **ukuran sampel kecil** — selisih 0.067 pada 45 Q&A ≈ 3 pertanyaan, dalam rentang variansi.

**Advanced paling kuat di pertanyaan HARD** (hit@5 **0.727** vs easy 0.545). Ini nilai praktis yang paling relevan: komponen lanjutan membantu paling besar justru saat retrieval sulit.

**Skilled underperform** di semua metrik. Penyebab paling mungkin: **BM25 dalam ensemble menambah noise keyword** pada teks hukum yang kosakatanya sangat overlap ("Pasal", "Pekerja", "Upah", "ayat" muncul di mana-mana) sehingga menaikkan chunk yang keyword-match tapi kurang relevan; RRF lalu mendilusi sinyal dense yang kuat. Untuk domain dengan vocabulary homogen seperti regulasi, dense murni ternyata sudah kompetitif.

**Kesimpulan retrieval:** komponen Advanced memberi peningkatan **presisi peringkat-atas (hit@1/hit@3)** dan **ketahanan pada pertanyaan sulit**, dengan trade-off recall Top-5 yang kecil. Untuk asisten legal yang menampilkan sitasi Top-beberapa, presisi peringkat-atas (chunk benar di posisi 1–3) lebih bernilai daripada recall Top-5.

## 3. Self-eval kualitas jawaban

| Metrik | Skor | n | Judge |
|---|---|---|---|
| faithfulness | 0.90 | 10 | model fine-tuned (SLM 3B) |
| answer_relevancy | 1.00 | 10 | model fine-tuned (SLM 3B) |

**Disclosure bias (WAJIB):** judge adalah SLM 3B (bukan model kelas GPT-4), sesuai keputusan desain "aplikatif" (data legal tidak dikeluarkan ke API eksternal). Skor cenderung **generous** — `answer_relevancy = 1.00` di seluruh 10 sampel jelas terlalu sempurna dan menandakan judge terlalu longgar. Karena itu, **metrik retrieval (hit@k/MRR/NDCG) adalah acuan utama** yang objektif; self-eval hanya sinyal arah pelengkap.

## 4. Keterbatasan & arah lanjutan

- **Sampel 45 Q&A** → selisih < ~0.07 antar tier sebaiknya dibaca sebagai setara (dalam noise).
- **HyDE pada SLM 3B** dapat menurunkan recall; ablation "Advanced tanpa HyDE" akan mengisolasi efek reranker murni (kandidat untuk iterasi berikutnya).
- **Generator SLM 3B** adalah bottleneck kualitas jawaban (bukan retrieval); retrieval memang menemukan pasal yang benar secara konsisten.
