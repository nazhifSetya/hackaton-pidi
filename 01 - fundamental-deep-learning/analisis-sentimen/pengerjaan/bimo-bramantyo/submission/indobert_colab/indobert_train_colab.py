"""
indobert_train_colab.py
========================
Fine-tune IndoBERT (indobenchmark/indobert-base-p1) untuk klasifikasi
3 kelas sentimen (negatif/netral/positif) — Proyek Analisis Sentimen Shopee.

Dijalankan di Google Colab dengan runtime GPU T4:
  1. Runtime → Change runtime type → T4 GPU
  2. Upload file: `dataset_shopee_labeled.csv` (dari submission/)
  3. pip install transformers datasets accelerate torch scikit-learn
  4. python indobert_train_colab.py

Output:
  - indobert_metrics.json   → train/test accuracy + F1 + classification_report
  - indobert_history.json   → train/val loss & acc per epoch

Config aman untuk T4 (16 GB VRAM):
  - batch_size = 16
  - max_len   = 128
  - epochs    = 3 (fine-tune BERT tidak butuh banyak epoch)
  - fp16      = True
"""
import json
import os
import time

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (accuracy_score, classification_report,
                             f1_score)
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          get_linear_schedule_with_warmup)


# ── Config ──────────────────────────────────────────────────────────────────
DATA_PATH = "dataset_shopee_labeled.csv"     # upload dulu ke Colab
MODEL_NAME = "indobenchmark/indobert-base-p1"
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 3
LR = 2e-5
SEED = 42
LABEL_ORDER = ["negatif", "netral", "positif"]

# ── Reproducibility ─────────────────────────────────────────────────────────
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {DEVICE}")
if DEVICE.type == "cuda":
    print(f"  GPU  : {torch.cuda.get_device_name(0)}")
    print(f"  VRAM : {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB")

# ── Load data ───────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["text_clean", "label"])
df = df[df["text_clean"].astype(str).str.len() > 0].reset_index(drop=True)
print(f"Load labeled: {len(df):,} baris")
print(f"Distribusi:  {df['label'].value_counts().to_dict()}")

lbl2id = {l: i for i, l in enumerate(LABEL_ORDER)}
id2lbl = {i: l for l, i in lbl2id.items()}
df["y"] = df["label"].map(lbl2id)

X_tr, X_te, y_tr, y_te = train_test_split(
    df["text_clean"].tolist(),
    df["y"].tolist(),
    test_size=0.2,
    stratify=df["y"].tolist(),
    random_state=SEED,
)
print(f"Split 80/20 -> train {len(X_tr):,}  test {len(X_te):,}")

# ── Tokenizer + model ───────────────────────────────────────────────────────
print(f"\nLoad tokenizer + model: {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=len(LABEL_ORDER)
).to(DEVICE)


class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tok, max_len):
        self.texts, self.labels, self.tok, self.max_len = texts, labels, tok, max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tok(
            str(self.texts[idx]),
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


ds_tr = SentimentDataset(X_tr, y_tr, tokenizer, MAX_LEN)
ds_te = SentimentDataset(X_te, y_te, tokenizer, MAX_LEN)
dl_tr = DataLoader(ds_tr, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
dl_te = DataLoader(ds_te, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

# ── Optimizer + scheduler ───────────────────────────────────────────────────
optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
total_steps = len(dl_tr) * EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps
)

scaler = torch.cuda.amp.GradScaler() if DEVICE.type == "cuda" else None

# ── Training loop ───────────────────────────────────────────────────────────
history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}


def evaluate(dl):
    model.eval()
    tot_loss, all_preds, all_labels = 0.0, [], []
    with torch.no_grad():
        for batch in dl:
            batch = {k: v.to(DEVICE) for k, v in batch.items()}
            with torch.cuda.amp.autocast(enabled=(DEVICE.type == "cuda")):
                out = model(**batch)
            tot_loss += out.loss.item()
            all_preds.extend(out.logits.argmax(-1).cpu().tolist())
            all_labels.extend(batch["labels"].cpu().tolist())
    return tot_loss / len(dl), accuracy_score(all_labels, all_preds), all_labels, all_preds


print(f"\n=== Training {EPOCHS} epoch (batch={BATCH_SIZE}, max_len={MAX_LEN}, fp16={DEVICE.type=='cuda'}) ===")
t0 = time.time()
for ep in range(1, EPOCHS + 1):
    model.train()
    tot_loss, correct, total = 0.0, 0, 0
    for i, batch in enumerate(dl_tr):
        batch = {k: v.to(DEVICE) for k, v in batch.items()}
        optimizer.zero_grad()
        if scaler is not None:
            with torch.cuda.amp.autocast():
                out = model(**batch)
            scaler.scale(out.loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            out = model(**batch)
            out.loss.backward()
            optimizer.step()
        scheduler.step()
        tot_loss += out.loss.item()
        preds = out.logits.argmax(-1)
        correct += (preds == batch["labels"]).sum().item()
        total += batch["labels"].size(0)
        if (i + 1) % 100 == 0:
            print(f"  ep{ep} step {i+1}/{len(dl_tr)} loss={tot_loss/(i+1):.4f} acc={correct/total:.4f}")
    tr_loss = tot_loss / len(dl_tr)
    tr_acc = correct / total

    val_loss, val_acc, _, _ = evaluate(dl_te)
    history["train_loss"].append(tr_loss)
    history["train_acc"].append(tr_acc)
    history["val_loss"].append(val_loss)
    history["val_acc"].append(val_acc)
    print(f"[epoch {ep}] train loss={tr_loss:.4f} acc={tr_acc:.4f} | val loss={val_loss:.4f} acc={val_acc:.4f}")

elapsed = time.time() - t0
print(f"\nTraining selesai dalam {elapsed:.1f}s ({elapsed/60:.1f} menit)")

# ── Final metrics ───────────────────────────────────────────────────────────
print("\n=== FINAL EVALUATION ===")
tr_loss_f, tr_acc_f, tr_labels_f, tr_preds_f = evaluate(dl_tr)
te_loss_f, te_acc_f, te_labels_f, te_preds_f = evaluate(dl_te)

f1_macro = f1_score(te_labels_f, te_preds_f, average="macro")
report = classification_report(
    te_labels_f, te_preds_f, target_names=LABEL_ORDER, digits=4
)
print(f"Train accuracy : {tr_acc_f:.4f}")
print(f"Test  accuracy : {te_acc_f:.4f}")
print(f"F1-macro (test): {f1_macro:.4f}")
print(f"\nClassification Report (test):\n{report}")

# ── Save JSON ───────────────────────────────────────────────────────────────
metrics_out = {
    "model": MODEL_NAME,
    "config": {
        "batch_size": BATCH_SIZE,
        "max_len": MAX_LEN,
        "epochs": EPOCHS,
        "lr": LR,
        "seed": SEED,
        "fp16": DEVICE.type == "cuda",
    },
    "train_acc": tr_acc_f,
    "test_acc": te_acc_f,
    "f1_macro": f1_macro,
    "classification_report": report,
    "label_order": LABEL_ORDER,
    "n_train": len(X_tr),
    "n_test": len(X_te),
    "elapsed_sec": elapsed,
}

with open("indobert_metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics_out, f, indent=2, ensure_ascii=False)
with open("indobert_history.json", "w", encoding="utf-8") as f:
    json.dump(history, f, indent=2)

print("\n[SAVED] indobert_metrics.json")
print("[SAVED] indobert_history.json")
print("\n>>> DOWNLOAD kedua file JSON dari Colab, taruh di folder submission/indobert_colab/")
