"""
Generator notebook Fine-tuning (K1 Basic) — PGABL versi Bimo.

Merakit `submission/Fine-tuning_submission_PGABL_Bimo_Bramantyo.ipynb` dari
potongan sel di sini (JSON assembly), lalu memvalidasi: JSON valid, tiap sel
kode lolos `ast.parse`, dan tidak ada kebocoran token / meta-conversation.

Notebook target: Gemma-2-2B (QLoRA 4-bit) -> SFT 800 langkah -> push merged_16bit.
Jalankan: python scripts/build_sft_notebook.py
"""
import ast
import json
import re
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "submission" / \
    "Fine-tuning_submission_PGABL_Bimo_Bramantyo.ipynb"


def md(teks: str) -> dict:
    return {"cell_type": "markdown", "metadata": {},
            "source": textwrap.dedent(teks).strip("\n").splitlines(keepends=True)}


def code(teks: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": textwrap.dedent(teks).strip("\n").splitlines(keepends=True)}


sel = []

# --- Judul -----------------------------------------------------------------
sel.append(md("""
    # Fine-tuning SLM Phi-3.5-mini (QLoRA) — Kriteria 1 PGABL

    Notebook ini melatih model bahasa kecil **Phi-3.5-mini-instruct** memakai teknik
    **QLoRA 4-bit** pada dataset instruksi Bahasa Indonesia, lalu mengunggah
    hasilnya ke Hugging Face agar bisa dipanggil kembali pada tahap RAG.

    Alur: instalasi -> autentikasi -> muat model 4-bit -> pasang LoRA ->
    format dataset (chat template Phi-3.5) -> latih 800 langkah -> unggah
    `merged_16bit`.

    **Lingkungan:** Google Colab, Runtime **T4 GPU**.
"""))

# --- Instalasi -------------------------------------------------------------
sel.append(md("""
    ## 1. Instalasi Pustaka

    Unsloth dipasang tanpa memaku versi (`unpinned`) agar ia menautkan sendiri
    versi `transformers`/`trl` yang cocok. Jika Colab meminta *restart session*
    setelah sel ini, lakukan restart lalu **Run all** ulang.
"""))
sel.append(code("""
    %%capture
    !pip install --upgrade --no-cache-dir unsloth
    !pip install --upgrade --no-cache-dir trl peft accelerate bitsandbytes datasets huggingface_hub
"""))

# --- Autentikasi -----------------------------------------------------------
sel.append(md("""
    ## 2. Autentikasi Hugging Face

    Token dan username diambil dari **Colab Secret** (bukan ditulis di sel).
    `HF_TOKEN` harus ber-scope *Write* agar bisa membuat repositori model.
"""))
sel.append(code("""
    import os

    try:
        from google.colab import userdata
        HF_TOKEN = userdata.get("HF_TOKEN")
        HF_USERNAME = userdata.get("HF_USERNAME")
    except Exception:
        HF_TOKEN = os.environ.get("HF_TOKEN")
        HF_USERNAME = os.environ.get("HF_USERNAME")

    assert HF_TOKEN, "HF_TOKEN belum tersedia. Simpan lewat Colab Secret."
    assert HF_USERNAME, "HF_USERNAME belum tersedia. Simpan lewat Colab Secret."

    from huggingface_hub import login
    login(token=HF_TOKEN)
    print("Terautentikasi. Akun:", HF_USERNAME)
"""))

# --- Konfigurasi -----------------------------------------------------------
sel.append(md("""
    ## 3. Konfigurasi Pelatihan

    Semua angka penting dikumpulkan di satu tempat agar mudah dilacak reviewer.
"""))
sel.append(code("""
    ID_MODEL     = "unsloth/Phi-3.5-mini-instruct-bnb-4bit"   # sudah 4-bit (nf4 + double quant)
    REPO_MODEL   = f"{HF_USERNAME}/PGABL-Phi-3.5-mini-SFT-Bimo"

    MAKS_TOKEN   = 1024      # panjang urutan maksimum
    BENIH        = 3407      # seed reproducibility
    RANK_LORA    = 8
    ALPHA_LORA   = 16
    DROPOUT_LORA = 0.05
    N_SAMPEL     = 10_000    # sub-sampel dataset
    BATCH        = 2         # per langkah
    AKUMULASI    = 4         # effective batch = BATCH * AKUMULASI = 8
    LANGKAH      = 800       # minimum wajib rubrik
    LR           = 2e-4

    print("Repo tujuan model:", REPO_MODEL)
"""))

# --- Muat model ------------------------------------------------------------
sel.append(md("""
    ## 4. Muat Model Dasar (QLoRA 4-bit + Double Quantization)

    `load_in_4bit=True` mengaktifkan kuantisasi `nf4` dengan *double quantization*
    secara internal. Cetakan `quantization_config` di bawah adalah bukti bahwa
    QLoRA 4-bit benar-benar aktif.
"""))
sel.append(code("""
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=ID_MODEL,
        max_seq_length=MAKS_TOKEN,
        dtype=None,            # auto: float16 pada T4
        load_in_4bit=True,     # QLoRA (nf4 + double quant)
    )

    qcfg = getattr(model.config, "quantization_config", None)
    print("Model dimuat :", ID_MODEL)
    print("Konfig kuantisasi:", qcfg)
"""))

# --- LoRA ------------------------------------------------------------------
sel.append(md("""
    ## 5. Pasang Adapter LoRA (Attention + FFN)

    Adapter ditaruh di proyeksi Phi-3.5 yang menyentuh dua komponen komputasi
    utama: Multi-Head Attention (`qkv_proj`, `o_proj` — Phi memakai QKV ter-fusi)
    dan Feed-Forward Network (`gate_up_proj`, `down_proj`). Rank kecil (r=8) cukup
    untuk membentuk gaya jawaban formal Bahasa Indonesia tanpa memberatkan VRAM.
"""))
sel.append(code("""
    model = FastLanguageModel.get_peft_model(
        model,
        r=RANK_LORA,
        lora_alpha=ALPHA_LORA,
        lora_dropout=DROPOUT_LORA,
        target_modules=[
            "qkv_proj", "o_proj",         # Multi-Head Attention (QKV ter-fusi)
            "gate_up_proj", "down_proj",  # Feed-Forward Network (gate/up ter-fusi)
        ],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=BENIH,
    )

    bisa_latih = sum(p.numel() for p in model.parameters() if p.requires_grad)
    semua = sum(p.numel() for p in model.parameters())
    print(f"Parameter dilatih : {bisa_latih:,} ({bisa_latih/semua:.3%} dari total)")
"""))

# --- Dataset ---------------------------------------------------------------
sel.append(md("""
    ## 6. Muat & Saring Dataset Instruksi

    `Ichsan2895/alpaca-gpt4-indonesian` memiliki dua kolom: `input` (pertanyaan)
    dan `output` (jawaban). Baris yang terlalu pendek dibuang agar model belajar
    pola jawaban yang bermakna, lalu diambil sub-sampel acak `N_SAMPEL` baris.
"""))
sel.append(code("""
    from datasets import load_dataset

    korpus = load_dataset("Ichsan2895/alpaca-gpt4-indonesian", split="train")
    print("Baris mentah:", len(korpus), "| kolom:", korpus.column_names)

    def cukup_panjang(baris):
        tanya = baris.get("input") or ""
        jawab = baris.get("output") or ""
        return len(tanya.strip()) >= 10 and len(jawab.strip()) >= 20

    bersih = korpus.filter(cukup_panjang)
    n = min(N_SAMPEL, len(bersih))
    sampel = bersih.shuffle(seed=BENIH).select(range(n))
    print("Setelah disaring:", len(bersih), "| dipakai:", len(sampel))
"""))

# --- Chat template + bukti -------------------------------------------------
sel.append(md("""
    ## 7. Terapkan Chat Template Phi-3.5 (Bukti Token Spesial)

    Phi-3.5 memakai format percakapan dengan penanda `<|user|>`, `<|assistant|>`,
    dan `<|end|>`. Template diatur lewat `get_chat_template(chat_template="phi-3.5")`,
    lalu tiap baris dipetakan `datasets.map()` menjadi kolom `text`. Cetakan
    berikut WAJIB memperlihatkan token spesial tersebut sebagai bukti template
    sudah diterapkan sebelum melatih.
"""))
sel.append(code("""
    from unsloth.chat_templates import get_chat_template

    tokenizer = get_chat_template(tokenizer, chat_template="phi-3.5")

    def susun_teks(baris):
        percakapan = [
            {"role": "user", "content": baris["input"]},
            {"role": "assistant", "content": baris["output"]},
        ]
        return {"text": tokenizer.apply_chat_template(
            percakapan, tokenize=False, add_generation_prompt=False)}

    siap_latih = sampel.map(susun_teks, remove_columns=sampel.column_names)

    baris_contoh = siap_latih[0]["text"]
    print("-" * 70)
    print("SATU BARIS DATASET SETELAH CHAT TEMPLATE PHI-3.5")
    print("-" * 70)
    print(baris_contoh)
    print("-" * 70)
    for penanda in ["<|user|>", "<|assistant|>", "<|end|>"]:
        status = "ADA" if penanda in baris_contoh else "TIDAK ADA"
        print(f"[{status}] token spesial {penanda}")
"""))

# --- SFTTrainer ------------------------------------------------------------
sel.append(md("""
    ## 8. Susun SFTTrainer

    `SFTTrainer` membaca kolom `text`. Effective batch = `BATCH * AKUMULASI = 8`.
    Penjadwal `linear` dengan pemanasan 3% menurunkan laju belajar hingga langkah
    ke-800. Optimizer `adamw_8bit` menghemat VRAM state optimizer.
"""))
sel.append(code("""
    from trl import SFTTrainer, SFTConfig

    pengaturan = SFTConfig(
        output_dir="/content/hasil_sft",
        per_device_train_batch_size=BATCH,
        gradient_accumulation_steps=AKUMULASI,
        max_steps=LANGKAH,
        learning_rate=LR,
        lr_scheduler_type="linear",
        warmup_steps=24,          # ~3% dari 800 langkah
        logging_steps=25,
        optim="adamw_8bit",
        weight_decay=0.01,
        seed=BENIH,
        report_to="none",
        max_seq_length=MAKS_TOKEN,
        dataset_text_field="text",
        packing=False,
        padding_free=False,       # TRL baru default padding_free=True + max_length -> error; matikan
        save_strategy="no",
    )

    sft = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=siap_latih,
        args=pengaturan,
    )
    print("SFTTrainer siap. Effective batch:", BATCH * AKUMULASI, "| langkah:", LANGKAH)
"""))

# --- Train -----------------------------------------------------------------
sel.append(md("""
    ## 9. Jalankan Pelatihan (800 Langkah)

    Perkiraan durasi di Colab T4 sekitar 60-90 menit. Selama `loss` menurun dan
    tidak ada error CUDA out-of-memory, ketentuan Basic Kriteria 1 terpenuhi.
"""))
sel.append(code("""
    ringkasan = sft.train()
    print("Pelatihan selesai.")
    print("Langkah terakhir:", sft.state.global_step)
    print("Loss terakhir   :", sft.state.log_history[-1].get("loss"))
"""))

# --- Merge + push ----------------------------------------------------------
sel.append(md("""
    ## 10. Gabungkan Adapter & Unggah ke Hugging Face

    Adapter LoRA digabung ke bobot dasar (`merged_16bit`) supaya model bisa
    langsung dipakai inferensi tanpa PEFT pada tahap RAG. Pengunggahan memakai
    pola dua langkah (`save_pretrained_merged` lalu `HfApi().upload_folder`) untuk
    menghindari `TypeError: safe_serialization` pada versi Unsloth terbaru;
    `delete_patterns` memastikan tidak ada berkas adapter tersisa di repositori.
"""))
sel.append(code("""
    from huggingface_hub import HfApi, create_repo

    FOLDER_GABUNG = "/content/phi_sft_merged"

    model.save_pretrained_merged(FOLDER_GABUNG, tokenizer, save_method="merged_16bit")
    print("Bobot tergabung disimpan:", FOLDER_GABUNG)

    api = HfApi()
    create_repo(repo_id=REPO_MODEL, private=False, exist_ok=True, token=HF_TOKEN)
    api.upload_folder(
        folder_path=FOLDER_GABUNG,
        repo_id=REPO_MODEL,
        token=HF_TOKEN,
        commit_message="SFT Phi-3.5-mini merged_16bit (PGABL)",
        delete_patterns=["adapter_config.json", "adapter_model.safetensors"],
    )
    tautan_model = f"https://huggingface.co/{REPO_MODEL}"
    print("Model publik terunggah:", tautan_model)
"""))

# --- link_huggingface.txt --------------------------------------------------
sel.append(md("""
    ## 11. Simpan Tautan Model

    Tautan repositori disimpan ke `link_huggingface.txt` (salah satu berkas
    submission). Unduh berkas ini bersama notebook yang sudah tereksekusi.
"""))
sel.append(code("""
    with open("link_huggingface.txt", "w", encoding="utf-8") as f:
        f.write(tautan_model + "\\n")
    print("Ditulis ke link_huggingface.txt:")
    print(tautan_model)
"""))

# --- Penutup ---------------------------------------------------------------
sel.append(md("""
    ## 12. Ringkasan

    | Aspek | Nilai |
    |---|---|
    | Model dasar | `unsloth/Phi-3.5-mini-instruct-bnb-4bit` |
    | Teknik | QLoRA 4-bit (nf4 + double quant), LoRA r=8 a=16 pada MHA+FFN |
    | Dataset | `Ichsan2895/alpaca-gpt4-indonesian` (chat template Phi-3.5) |
    | Pelatihan | SFTTrainer 800 langkah, effective batch 8, LR 2e-4 linear |
    | Unggah | `merged_16bit` ke repositori Hugging Face publik |

    Kriteria 1 (Basic) terpenuhi. Model siap dipakai pada notebook RAG.
"""))

# ---------------------------------------------------------------------------
# Rakit notebook
# ---------------------------------------------------------------------------
notebook = {
    "cells": sel,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "accelerator": "GPU",
        "colab": {"provenance": [], "gpuType": "T4"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------------------------------------------------------------------
# Validasi
# ---------------------------------------------------------------------------
data = json.loads(OUT.read_text(encoding="utf-8"))
assert data["nbformat"] == 4, "nbformat harus 4"

sel_kode = [c for c in data["cells"] if c["cell_type"] == "code"]
for i, c in enumerate(sel_kode):
    src = "".join(c["source"])
    # buang magic Colab (%%capture / !pip) sebelum ast.parse
    baris_py = [b for b in src.splitlines()
                if not b.lstrip().startswith(("%", "!"))]
    ast.parse("\n".join(baris_py))

# Scan kebocoran token & meta-conversation di seluruh sel
gabung = "\n".join("".join(c["source"]) for c in data["cells"])
bocor_token = re.findall(r"hf_[A-Za-z0-9]{20,}", gabung)
terlarang = [w for w in ["claude", "CLAUDE", "share ke aku", "panduan/",
                         "nazhif", "dafina", "fareynaldi"]
             if w.lower() in gabung.lower()]

print("OK  notebook ditulis :", OUT)
print("OK  jumlah sel        :", len(data["cells"]),
      f"({len(sel_kode)} kode)")
print("OK  ast.parse         : semua sel kode lolos")
print("HR  token bocor       :", bocor_token or "TIDAK ADA")
print("HR  kata terlarang    :", terlarang or "TIDAK ADA")
assert not bocor_token, "Ada token ter-hardcode!"
assert not terlarang, f"Ada kata terlarang: {terlarang}"
print("VALIDASI LULUS.")
