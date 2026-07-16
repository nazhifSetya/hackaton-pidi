"""
Builder: generate submission/Fine-tuning_submission_PGABL_fareynaldi_affan.ipynb

Design principles (BASIC tier, independen dari implementasi rekan):
- Alur linear single-experiment (tanpa hyperparameter search).
- Cell modular per-tahap: install -> auth -> load model -> LoRA -> dataset ->
  chat-template + BUKTI special tokens -> SFT 800 steps -> push merged_16bit.
- Semua magic number hardcoded di notebook agar self-contained
  (tanpa dependency ke src/ atau configs/ saat reviewer Run All).
- Pola push 2-langkah: save_pretrained_merged + HfApi.upload_folder
  (hindari bug TypeError safe_serialization di Unsloth 2026.7.x).
- Anti-plagiarisme: struktur, naming, hyperparameter, narasi berbeda.
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "Fine-tuning_submission_PGABL_fareynaldi_affan.ipynb"


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": _to_lines(source),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _to_lines(source),
    }


def _to_lines(text: str) -> list[str]:
    text = dedent(text).strip("\n")
    lines = text.split("\n")
    return [ln + "\n" for ln in lines[:-1]] + [lines[-1]]


cells: list[dict] = []

# =====================================================================
# 1. Header + konteks
# =====================================================================
cells.append(md("""
    # Fine-tuning SLM Llama-3.2-3B — Submission PGABL

    **Proyek:** Asisten AI internal tim legal berbasis SLM fine-tuned + RAG.
    **Notebook ini:** *Kriteria 1 — Fine-tuning LLM Anda Sendiri* (Basic).

    Notebook ini melakukan supervised fine-tuning (SFT) dengan pipeline berikut:

    1. Load base model `unsloth/Llama-3.2-3B-Instruct` dalam mode **4-bit QLoRA
       double quantization**.
    2. Pasang adapter **LoRA** pada seluruh proyeksi Multi-Head Attention
       (`q,k,v,o`) + Feed-Forward Network (`gate,up,down`).
    3. Load dataset instruksi Bahasa Indonesia `Ichsan2895/alpaca-gpt4-indonesian`,
       konversi ke format chat **Llama-3** via `datasets.map()`,
       lalu tampilkan satu contoh baris lengkap dengan special token.
    4. Jalankan `SFTTrainer` selama **800 steps**.
    5. Merge adapter ke bobot base kemudian upload ke Hugging Face Hub sebagai
       repositori publik `merged_16bit`.

    Model hasil fine-tuning inilah yang dipakai sebagai generator pada pipeline
    RAG di notebook berikutnya.
"""))

# =====================================================================
# 2. Panduan environment Colab
# =====================================================================
cells.append(md("""
    ## 0. Panduan Environment

    - **Runtime:** Google Colab, `Runtime → Change runtime type → T4 GPU`
      (free tier, 16 GB VRAM). Local GPU 4–8 GB tidak cukup untuk 800-step SFT
      pada model 3B parameter.
    - **Secrets Colab** (ikon kunci di sidebar kiri):
        - `HF_TOKEN` — Hugging Face token dengan role **Write** untuk push model.
        - `HF_USERNAME` — username Hugging Face untuk pemilik repositori.
      Aktifkan toggle *Notebook access* pada kedua secret.
    - **Reproduksibilitas:** semua random ops diseed pada `42`.
    - Kalau di tengah instalasi cell menampilkan pesan minta *restart runtime*,
      jalankan `Runtime → Restart runtime` lalu **Run All** ulang.
"""))

# =====================================================================
# 3. Install dependencies
# =====================================================================
cells.append(code("""
    # Instalasi stack Unsloth. Sengaja TIDAK di-pin manual untuk transformers /
    # trl / datasets karena Unsloth versi terbaru menuntut transformers >= 4.51
    # dan pin manual sering memicu ImportError CompileConfig.
    !pip install -q --upgrade pip
    !pip install -q "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" bitsandbytes accelerate peft trl datasets huggingface_hub
"""))

# =====================================================================
# 4. Auth HF
# =====================================================================
cells.append(md("""
    ## 1. Otentikasi Hugging Face

    Kredensial dibaca dari Colab Secrets — **tidak boleh** ditulis literal pada
    notebook. Kalau salah satu secret hilang, cell berikut akan gagal dengan
    pesan yang jelas.
"""))

cells.append(code("""
    import os
    from google.colab import userdata
    from huggingface_hub import login, whoami

    HF_TOKEN = userdata.get("HF_TOKEN")
    HF_USERNAME = userdata.get("HF_USERNAME")

    assert HF_TOKEN, "HF_TOKEN belum di-set di Colab Secrets"
    assert HF_USERNAME, "HF_USERNAME belum di-set di Colab Secrets"

    os.environ["HF_TOKEN"] = HF_TOKEN
    login(token=HF_TOKEN, add_to_git_credential=False)

    identity = whoami(token=HF_TOKEN)
    print("Login sebagai:", identity.get("name"))
    print("Akun aktif   :", HF_USERNAME)
"""))

# =====================================================================
# 5. Konstanta konfigurasi (self-contained, tanpa YAML external)
# =====================================================================
cells.append(md("""
    ## 2. Konfigurasi Pelatihan

    Nilai-nilai berikut dipilih agar 800 langkah training aman berjalan pada
    Colab T4 (16 GB VRAM) untuk Llama-3.2-3B parameter dalam mode 4-bit QLoRA.
    Ukuran sequence 1024 token menutup mayoritas pasangan Q&A pada dataset
    `alpaca-gpt4-indonesian`.
"""))

cells.append(code("""
    SEED = 42
    BASE_MODEL_ID = "unsloth/Llama-3.2-3B-Instruct"
    MAX_SEQ_LENGTH = 1024
    LORA_RANK = 8
    LORA_ALPHA = 16
    LORA_DROPOUT = 0.05
    LEARNING_RATE = 3e-4
    TRAIN_STEPS = 800
    PER_DEVICE_BATCH = 2
    GRAD_ACCUM = 4
    WARMUP_STEPS = 25
    LOG_STEPS = 20
    DATASET_SUBSET = 12_000

    import random, numpy as np, torch
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

    HF_REPO_NAME = "PGABL-Llama-3.2-3B-SFT-Fareynaldi"
    HF_REPO_ID = f"{HF_USERNAME}/{HF_REPO_NAME}"
    print("Repo tujuan   :", HF_REPO_ID)
    print("GPU tersedia  :", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
"""))

# =====================================================================
# 6. Load base model 4-bit
# =====================================================================
cells.append(md("""
    ## 3. Muat Base Model (QLoRA 4-bit)

    Unsloth menggabungkan `bitsandbytes` NF4 + double quantization dalam satu
    pemanggilan `FastLanguageModel.from_pretrained`. Compute dtype `bfloat16`
    dipilih untuk kompatibilitas T4.
"""))

cells.append(code("""
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL_ID,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,           # auto-detect (bfloat16 pada T4)
        load_in_4bit=True,    # QLoRA
    )

    print("Model      :", BASE_MODEL_ID)
    print("Max seq len:", MAX_SEQ_LENGTH)
    print("Load in 4bit: True (nf4 + double quant otomatis dari Unsloth)")
"""))

# =====================================================================
# 7. Attach LoRA MHA + FFN
# =====================================================================
cells.append(md("""
    ## 4. Pasang Adapter LoRA (MHA + FFN)

    LoRA dipasang pada tujuh proyeksi berikut agar mencakup dua komponen
    komputasi utama Transformer, yakni **Multi-Head Attention** (`q_proj,
    k_proj, v_proj, o_proj`) dan **Feed-Forward Network** (`gate_proj, up_proj,
    down_proj`). Konfigurasi rank rendah (r=8) sudah cukup untuk membentuk gaya
    respons formal Bahasa Indonesia tanpa membebani VRAM.
"""))

cells.append(code("""
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_RANK,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",   # Multi-Head Attention
            "gate_proj", "up_proj", "down_proj",       # Feed-Forward Network
        ],
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=SEED,
    )

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Trainable params : {trainable:,}")
    print(f"Total params     : {total:,}")
    print(f"Trainable ratio  : {trainable/total:.4%}")
"""))

# =====================================================================
# 8. Load dataset
# =====================================================================
cells.append(md("""
    ## 5. Muat Dataset Instruksi Bahasa Indonesia

    Dataset `Ichsan2895/alpaca-gpt4-indonesian` memiliki dua kolom saja:
    `input` (pertanyaan/instruksi) dan `output` (jawaban). Kita saring baris
    yang terlalu pendek supaya SFT belajar pola respons yang bermakna, lalu
    ambil sub-sampel `DATASET_SUBSET` baris — jumlah tersebut cukup untuk
    memenuhi 800 langkah training dengan effective batch 8.
"""))

cells.append(code("""
    from datasets import load_dataset

    raw = load_dataset("Ichsan2895/alpaca-gpt4-indonesian", split="train")
    print("Jumlah baris mentah :", len(raw))
    print("Kolom               :", raw.column_names)

    def _has_content(row):
        return (
            isinstance(row.get("input"), str) and len(row["input"]) >= 5
            and isinstance(row.get("output"), str) and len(row["output"]) >= 20
        )

    clean = raw.filter(_has_content)
    print("Setelah filter      :", len(clean))

    subset = clean.shuffle(seed=SEED).select(range(min(DATASET_SUBSET, len(clean))))
    print("Sub-sampel dipakai  :", len(subset))
    print("Contoh input        :", subset[0]["input"][:120], "...")
    print("Contoh output       :", subset[0]["output"][:120], "...")
"""))

# =====================================================================
# 9. Apply chat template Llama-3 + BUKTI special tokens (RUBRIC WAJIB)
# =====================================================================
cells.append(md("""
    ## 6. Terapkan Chat Template Llama-3 (Bukti Special Token)

    Dataset dikonversi ke format percakapan Llama-3 melalui
    `datasets.map()` dan `tokenizer.apply_chat_template`. Pada cetakan
    setelah mapping harus terlihat token khusus khas Llama-3
    (`<|begin_of_text|>`, `<|start_header_id|>`, `<|end_header_id|>`,
    `<|eot_id|>`) — ini bukti wajib bahwa chat template sudah dipakai
    sebelum training.
"""))

cells.append(code("""
    from unsloth.chat_templates import get_chat_template

    tokenizer = get_chat_template(tokenizer, chat_template="llama-3")

    def to_llama3_chat(row):
        messages = [
            {"role": "user",      "content": row["input"]},
            {"role": "assistant", "content": row["output"]},
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        return {"text": text}

    formatted = subset.map(to_llama3_chat, remove_columns=subset.column_names)

    print("=" * 70)
    print("CONTOH BARIS DATASET SETELAH APPLY CHAT TEMPLATE LLAMA-3")
    print("=" * 70)
    print(formatted[0]["text"])
    print("=" * 70)

    required_tokens = [
        "<|begin_of_text|>",
        "<|start_header_id|>",
        "<|end_header_id|>",
        "<|eot_id|>",
    ]
    sample = formatted[0]["text"]
    for tok in required_tokens:
        status = "OK" if tok in sample else "MISSING"
        print(f"[{status}] {tok}")
"""))

# =====================================================================
# 10. SFTTrainer configuration
# =====================================================================
cells.append(md("""
    ## 7. Konfigurasi SFTTrainer

    `SFTTrainer` mengambil kolom `text` yang sudah kita bentuk. Effective batch
    = `per_device_batch * grad_accum = 2 * 4 = 8`. Optimizer `adamw_8bit`
    dipilih untuk menekan pemakaian VRAM optimizer state.
"""))

cells.append(code("""
    from trl import SFTTrainer, SFTConfig

    trainer_args = SFTConfig(
        output_dir="/content/sft_ckpt",
        per_device_train_batch_size=PER_DEVICE_BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        warmup_steps=WARMUP_STEPS,
        max_steps=TRAIN_STEPS,
        learning_rate=LEARNING_RATE,
        logging_steps=LOG_STEPS,
        optim="adamw_8bit",
        lr_scheduler_type="linear",
        weight_decay=0.01,
        seed=SEED,
        report_to="none",
        max_seq_length=MAX_SEQ_LENGTH,
        dataset_text_field="text",
        packing=False,
        save_strategy="no",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=formatted,
        args=trainer_args,
    )
    print("SFTTrainer siap dijalankan.")
    print("Effective batch     :", PER_DEVICE_BATCH * GRAD_ACCUM)
    print("Total training steps:", TRAIN_STEPS)
"""))

# =====================================================================
# 11. Train
# =====================================================================
cells.append(md("""
    ## 8. Jalankan Training

    Estimasi durasi pada Colab T4: sekitar 90–120 menit untuk 800 langkah.
    Panel `loss` akan menurun bertahap; asal turun konsisten dan tidak muncul
    error CUDA OOM, kriteria Basic sudah terpenuhi.
"""))

cells.append(code("""
    train_result = trainer.train()
    print("Training selesai.")
    print("Global step akhir :", trainer.state.global_step)
    print("Loss akhir        :", trainer.state.log_history[-1].get("loss"))
"""))

# =====================================================================
# 12. Save merged + push (pattern 2-langkah)
# =====================================================================
cells.append(md("""
    ## 9. Merge Adapter dan Push ke Hugging Face

    Adapter LoRA di-*merge* ke bobot base sehingga model dapat dipakai langsung
    untuk inferensi tanpa PEFT. Pengunggahan dilakukan dengan pola dua langkah
    (`save_pretrained_merged` lalu `HfApi().upload_folder`) untuk menghindari
    bug `TypeError: safe_serialization` yang muncul pada
    `push_to_hub_merged` versi Unsloth terbaru.
"""))

cells.append(code("""
    from huggingface_hub import HfApi, create_repo

    MERGED_DIR = "/content/sft_merged_16bit"

    model.save_pretrained_merged(
        MERGED_DIR,
        tokenizer,
        save_method="merged_16bit",
    )
    print("Merged model tersimpan di:", MERGED_DIR)

    api = HfApi()
    create_repo(repo_id=HF_REPO_ID, private=False, exist_ok=True, token=HF_TOKEN)
    api.upload_folder(
        folder_path=MERGED_DIR,
        repo_id=HF_REPO_ID,
        token=HF_TOKEN,
        commit_message="Upload SFT merged_16bit — PGABL Fareynaldi",
        delete_patterns=[
            "adapter_config.json",
            "adapter_model.safetensors",
        ],
    )
    hf_url = f"https://huggingface.co/{HF_REPO_ID}"
    print("Model terupload:", hf_url)
"""))

# =====================================================================
# 13. Tulis link_huggingface.txt
# =====================================================================
cells.append(md("""
    ## 10. Simpan Tautan Repositori Hugging Face

    File `link_huggingface.txt` dijadikan bagian deliverable submission — berisi
    URL model hasil fine-tuning yang nanti dipanggil pada notebook RAG.
"""))

cells.append(code("""
    link_path = "/content/link_huggingface.txt"
    with open(link_path, "w", encoding="utf-8") as f:
        f.write(hf_url + "\\n")
    print("Isi", link_path, ":")
    print(open(link_path).read())
"""))

# =====================================================================
# 14. Ringkasan
# =====================================================================
cells.append(md("""
    ## 11. Ringkasan

    | Item | Nilai |
    |------|-------|
    | Base model | `unsloth/Llama-3.2-3B-Instruct` (4-bit QLoRA, nf4 + double quant) |
    | Adapter LoRA | r=8, α=16, dropout=0.05 pada `q,k,v,o,gate,up,down` (MHA + FFN) |
    | Dataset SFT | `Ichsan2895/alpaca-gpt4-indonesian` (subset 12k baris) |
    | Chat template | Llama-3 (via `datasets.map()` + `apply_chat_template`) |
    | Training steps | 800 (effective batch 8) |
    | Push method | `merged_16bit` via `save_pretrained_merged` + `HfApi.upload_folder` |
    | Output artefak | Repo HF publik + `link_huggingface.txt` |

    Model publik ini akan dipanggil kembali sebagai *generator* pada notebook
    RAG (`RAG_submission_PGABL_fareynaldi_affan.ipynb`).
"""))

# =====================================================================
# Serialise
# =====================================================================
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.11",
        },
        "accelerator": "GPU",
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Notebook Fine-tuning ditulis: {OUT}")
print(f"Jumlah cell: {len(cells)}")
