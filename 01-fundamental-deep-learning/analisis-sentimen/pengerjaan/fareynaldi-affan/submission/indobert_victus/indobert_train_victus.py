"""
indobert_train_victus.py  —  SKEMA 4: Fine-tune IndoBERT (dijalankan di HP Victus / GPU CUDA)
=============================================================================================
Analisis Sentimen ulasan MyTelkomsel (3 kelas: negatif / netral / positif).

DIJALANKAN DI: HP Victus (NVIDIA RTX 3050, 4GB VRAM), Windows + CUDA.
INPUT : dataset_mytelkomsel_labeled.csv  (kolom: text_clean, label)
OUTPUT: indobert_metrics.json + indobert_history.json  -> dikirim balik ke M1.

Config aman 4GB VRAM: batch 8, max_len 128, fp16, gradient_checkpointing.
Kalau OOM: turunkan BATCH ke 4, atau MODEL_NAME ke "indobenchmark/indobert-lite-base-p1".

Skema evaluasi (BERSIH, tanpa kebocoran data / anti data-leak):
  data -> train(80%) / test(20%).  train -> train2(90%) / val(10%).
  Model dipilih dari epoch dgn akurasi VAL terbaik, lalu dievaluasi SEKALI di TEST.
  (Tokenizer BERT sudah pretrained -> tidak ada 'fit' di test, jadi tidak ada leak.)
"""

import json
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, f1_score, classification_report,
                             confusion_matrix)
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          TrainingArguments, Trainer, DataCollatorWithPadding,
                          set_seed)

# ─────────────────────────── CONFIG ───────────────────────────
CSV_PATH   = "dataset_mytelkomsel_labeled.csv"
TEXT_COL   = "text_clean"
LABEL_COL  = "label"
MODEL_NAME = "indobenchmark/indobert-base-p1"   # fallback ringan: "indobenchmark/indobert-lite-base-p1"
MAX_LEN    = 128
BATCH      = 8          # turunkan ke 4 kalau OOM
GRAD_ACCUM = 2          # effective batch = 16
EPOCHS     = 4
LR         = 2e-5
SEED       = 42
set_seed(SEED)

LABELS = ["negatif", "netral", "positif"]
l2id = {l: i for i, l in enumerate(LABELS)}
id2l = {i: l for l, i in l2id.items()}

# ─────────────────────────── DATA ───────────────────────────
df = pd.read_csv(CSV_PATH).dropna(subset=[TEXT_COL, LABEL_COL])
df["labels"] = df[LABEL_COL].map(l2id)
X = df[TEXT_COL].astype(str).tolist()
y = df["labels"].tolist()

# train/test 80/20, lalu train -> train2/val 90/10 (val utk pilih model terbaik)
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y)
Xtr2, Xval, ytr2, yval = train_test_split(
    Xtr, ytr, test_size=0.1111, random_state=SEED, stratify=ytr)
print(f"train={len(Xtr2)} val={len(Xval)} test={len(Xte)} "
      f"device={'cuda' if torch.cuda.is_available() else 'CPU (!)'}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


def tok(batch):
    """Tokenisasi batch teks (truncation ke MAX_LEN)."""
    return tokenizer(batch["text"], truncation=True, max_length=MAX_LEN)


ds_tr  = Dataset.from_dict({"text": Xtr2, "labels": ytr2}).map(tok, batched=True)
ds_val = Dataset.from_dict({"text": Xval, "labels": yval}).map(tok, batched=True)
ds_te  = Dataset.from_dict({"text": Xte,  "labels": yte}).map(tok, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=3, id2label=id2l, label2id=l2id,
    use_safetensors=True,          # muat bobot .safetensors (hindari error torch.load pickle)
    ignore_mismatched_sizes=True)  # head klasifikasi 3 kelas di-inisiasi ulang (wajar utk fine-tune)
model.gradient_checkpointing_enable()


def metrics_fn(p):
    """Hitung accuracy & F1-macro dari prediksi Trainer."""
    preds = np.argmax(p.predictions, axis=1)
    return {"accuracy": accuracy_score(p.label_ids, preds),
            "f1_macro": f1_score(p.label_ids, preds, average="macro")}


args = TrainingArguments(
    output_dir="indobert_ckpt",
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH,
    per_device_eval_batch_size=BATCH,
    gradient_accumulation_steps=GRAD_ACCUM,
    learning_rate=LR,
    fp16=torch.cuda.is_available(),
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=1,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    greater_is_better=True,
    logging_steps=50,
    report_to="none",
    seed=SEED,
)

trainer = Trainer(
    model=model, args=args,
    train_dataset=ds_tr, eval_dataset=ds_val,
    processing_class=tokenizer,                       # 'tokenizer=' sudah deprecated
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=metrics_fn,
)
train_out = trainer.train()


# ─────────────────────── EVALUASI (train & test) ───────────────────────
def eval_split(ds, y_true, name):
    """Prediksi satu split lalu cetak & kembalikan (acc, f1_macro, preds)."""
    pred = np.argmax(trainer.predict(ds).predictions, axis=1)
    acc = accuracy_score(y_true, pred)
    f1 = f1_score(y_true, pred, average="macro")
    print(f"== {name} == acc={acc:.4f} f1_macro={f1:.4f}")
    return acc, f1, pred


tr_acc, tr_f1, _ = eval_split(ds_tr, ytr2, "TRAIN")
te_acc, te_f1, te_pred = eval_split(ds_te, yte, "TEST")
report = classification_report(yte, te_pred, target_names=LABELS, digits=4)
cm = confusion_matrix(yte, te_pred).tolist()
print("\nCLASSIFICATION REPORT (test):\n", report)

metrics = {
    "model": MODEL_NAME, "max_len": MAX_LEN, "batch": BATCH, "grad_accum": GRAD_ACCUM,
    "epochs": EPOCHS, "n_train": len(Xtr2), "n_val": len(Xval), "n_test": len(Xte),
    "train_accuracy": tr_acc, "train_f1_macro": tr_f1,
    "test_accuracy": te_acc, "test_f1_macro": te_f1,
    "labels": LABELS, "confusion_matrix": cm, "classification_report": report,
}
with open("indobert_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
with open("indobert_history.json", "w") as f:
    json.dump(train_out.metrics if hasattr(train_out, "metrics") else {}, f, indent=2)
trainer.save_model("indobert_mytelkomsel_model")
tokenizer.save_pretrained("indobert_mytelkomsel_model")
print(f"\nSELESAI. Kirim balik indobert_metrics.json + indobert_history.json. "
      f"RINGKAS -> TEST acc={te_acc:.4f} f1={te_f1:.4f}")
