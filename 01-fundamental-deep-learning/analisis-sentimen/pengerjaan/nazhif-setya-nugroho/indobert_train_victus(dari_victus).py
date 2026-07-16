"""
indobert_train_victus.py  —  SKEMA 4: Fine-tune IndoBERT (dijalankan di HP Victus / GPU CUDA)
=============================================================================================
Analisis Sentimen ulasan PLN Mobile (3 kelas: negatif / netral / positif).

DIJALANKAN DI: HP Victus (NVIDIA RTX 3050, 4GB VRAM), Windows + CUDA.
(Claude tidak bisa remote ke device ini, jadi skrip ini kamu jalankan sendiri —
 lihat PANDUAN_VICTUS.md untuk langkah step-by-step.)

INPUT : dataset_pln_labeled.csv  (kolom: text_clean, label)  <- hasil labeling di M1
OUTPUT: - folder model tersimpan (indobert_pln_model/)
        - indobert_metrics.json  (accuracy & F1 train + test, classification report, confusion matrix)
        - indobert_history.json  (loss/acc per epoch)
        => 2 file JSON ini dikirim balik ke M1 untuk di-embed ke notebook.

Config aman untuk 4GB VRAM: batch 8, max_len 128, fp16, gradient_checkpointing.
Kalau tetap OOM (out of memory), turunkan BATCH ke 4 (EFFECTIVE tetap 16 via grad-accum),
atau ganti MODEL_NAME ke "indobenchmark/indobert-lite-base-p1".
"""

import json, numpy as np, pandas as pd, torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          TrainingArguments, Trainer, DataCollatorWithPadding, set_seed)

# ─────────────────────────── CONFIG ───────────────────────────
CSV_PATH   = "dataset_pln_labeled.csv"
TEXT_COL   = "text_clean"
LABEL_COL  = "label"
MODEL_NAME = "indobenchmark/indobert-base-p1"   # fallback ringan: "indobenchmark/indobert-lite-base-p1"
MAX_LEN    = 128
BATCH      = 8          # turunkan ke 4 kalau OOM
GRAD_ACCUM = 2          # effective batch = BATCH * GRAD_ACCUM = 16
EPOCHS     = 3
LR         = 2e-5
TEST_SIZE  = 0.2        # split 80/20
SEED       = 42
set_seed(SEED)

LABELS = ["negatif", "netral", "positif"]
l2id = {l: i for i, l in enumerate(LABELS)}
id2l = {i: l for l, i in l2id.items()}

# ─────────────────────────── DATA ───────────────────────────
df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=[TEXT_COL, LABEL_COL])
df["labels"] = df[LABEL_COL].map(l2id)

Xtr, Xte, ytr, yte = train_test_split(
    df[TEXT_COL].astype(str).tolist(), df["labels"].tolist(),
    test_size=TEST_SIZE, random_state=SEED, stratify=df["labels"].tolist())
print(f"train={len(Xtr)}  test={len(Xte)}  device={'cuda' if torch.cuda.is_available() else 'CPU (!)'}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
def tok(batch):
    return tokenizer(batch["text"], truncation=True, max_length=MAX_LEN)

ds_tr = Dataset.from_dict({"text": Xtr, "labels": ytr}).map(tok, batched=True)
ds_te = Dataset.from_dict({"text": Xte, "labels": yte}).map(tok, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=3, id2label=id2l, label2id=l2id,
    use_safetensors=True, ignore_mismatched_sizes=True)
model.gradient_checkpointing_enable()   # hemat VRAM

def metrics_fn(p):
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
    save_strategy="no",
    logging_steps=50,
    report_to="none",
    seed=SEED,
)

trainer = Trainer(
    model=model, args=args,
    train_dataset=ds_tr, eval_dataset=ds_te,
    processing_class=tokenizer, data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=metrics_fn,
)

train_out = trainer.train()

# ─────────────────────── EVALUASI (train & test) ───────────────────────
def eval_split(ds, y_true, name):
    pred = np.argmax(trainer.predict(ds).predictions, axis=1)
    acc = accuracy_score(y_true, pred); f1 = f1_score(y_true, pred, average="macro")
    print(f"\n== {name} ==  acc={acc:.4f}  f1_macro={f1:.4f}")
    return acc, f1, pred

tr_acc, tr_f1, _ = eval_split(ds_tr, ytr, "TRAIN")
te_acc, te_f1, te_pred = eval_split(ds_te, yte, "TEST")
report = classification_report(yte, te_pred, target_names=LABELS, digits=4)
cm = confusion_matrix(yte, te_pred).tolist()
print("\nCLASSIFICATION REPORT (test):\n", report)

# ─────────────────────── SIMPAN HASIL ───────────────────────
metrics = {
    "model": MODEL_NAME, "max_len": MAX_LEN, "batch": BATCH, "grad_accum": GRAD_ACCUM,
    "epochs": EPOCHS, "n_train": len(Xtr), "n_test": len(Xte),
    "train_accuracy": tr_acc, "train_f1_macro": tr_f1,
    "test_accuracy": te_acc, "test_f1_macro": te_f1,
    "labels": LABELS, "confusion_matrix": cm, "classification_report": report,
}
with open("indobert_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
with open("indobert_history.json", "w") as f:
    json.dump(train_out.metrics if hasattr(train_out, "metrics") else {}, f, indent=2)
trainer.save_model("indobert_pln_model")
tokenizer.save_pretrained("indobert_pln_model")
print("\nSELESAI. Kirim balik ke M1: indobert_metrics.json (+ indobert_history.json).")
print(f"RINGKAS -> TEST acc={te_acc:.4f}  f1={te_f1:.4f}")
