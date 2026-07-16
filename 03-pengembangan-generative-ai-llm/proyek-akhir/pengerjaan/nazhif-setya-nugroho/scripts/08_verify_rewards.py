"""VERIFY-FIRST: uji 4 reward function GRPO pada completion buatan.

Tujuan: pastikan tiap reward memberi skor yang MASUK AKAL (monoton ke arah yang
benar) sebelum kode di-inline ke notebook GRPO. Tidak butuh GPU / paket berat —
kalau rouge_score/langdetect tak ada, rewards.py otomatis pakai fallback.

Jalankan:  python3 scripts/08_verify_rewards.py
Output:    outputs/samples/reward_verify.json  (+ tabel ringkas ke stdout)
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from finetune import rewards as R  # noqa: E402

GT = (
    "Waktu kerja lembur hanya dapat dilakukan paling banyak 4 jam dalam 1 hari "
    "dan 18 jam dalam 1 minggu, dan pengusaha wajib membayar upah kerja lembur."
)

# reasoning ~300 char (dekat puncak kurva panjang)
THINK_GOOD = (
    "Pertanyaan menanyakan batas dan hak lembur. Saya perlu mengingat aturan waktu "
    "kerja lembur pada regulasi ketenagakerjaan: batas maksimal jam lembur per hari "
    "dan per minggu, serta kewajiban pengusaha membayar upah lembur. Saya rangkai "
    "jawaban ringkas dalam Bahasa Indonesia formal berdasarkan poin-poin itu."
)

CASES = [
    {
        "name": "A_ideal_id_think300",
        "text": f"<think>{THINK_GOOD}</think>\n{GT}",
        "expect": "format=1, length~tinggi, correctness tinggi, language=1",
    },
    {
        "name": "B_no_think_english",
        "text": "Overtime is capped at 4 hours per day and the employer must pay overtime wages.",
        "expect": "format=0, length=0, correctness rendah, language=-0.5",
    },
    {
        "name": "C_think_too_short_id",
        "text": "<think>lembur.</think>\nLembur maksimal 4 jam sehari dan pengusaha wajib membayar upah lembur.",
        "expect": "format=1, length rendah, correctness sedang, language=1",
    },
    {
        "name": "D_think_too_long_id",
        "text": "<think>" + ("Saya menganalisis aturan lembur secara sangat panjang. " * 25)
        + "</think>\nLembur maksimal 4 jam sehari.",
        "expect": "format=1, length turun (kepanjangan), language=1",
    },
    {
        "name": "E_conversational_format",
        "text": [{"role": "assistant", "content": f"<think>{THINK_GOOD}</think>\n{GT}"}],
        "expect": "sama seperti A (uji parsing format conversational)",
    },
]

completions = [c["text"] for c in CASES]
ground_truth = [GT] * len(CASES)

scores = {
    "format": R.format_reward_func(completions=completions),
    "reasoning_length": R.reasoning_length_reward(completions=completions),
    "correctness": R.correctness_reward(completions=completions, ground_truth=ground_truth),
    "language": R.language_reward_func(completions=completions),
}

# weighted total (seperti GRPOConfig.reward_weights)
w = dict(zip(["format", "reasoning_length", "correctness", "language"], R.REWARD_WEIGHTS))
weighted_total = [
    round(sum(scores[k][i] * w[k] for k in scores), 4) for i in range(len(CASES))
]

report = {
    "backends": R.BACKENDS,
    "reward_weights": w,
    "cases": [],
}
print(f"\nBackends: {R.BACKENDS}")
print(f"Weights : {w}\n")
header = f"{'case':26s} | {'format':>6s} | {'length':>6s} | {'correct':>7s} | {'lang':>5s} | {'W.total':>7s}"
print(header)
print("-" * len(header))
for i, c in enumerate(CASES):
    row = {
        "name": c["name"],
        "expect": c["expect"],
        "format": round(scores["format"][i], 4),
        "reasoning_length": round(scores["reasoning_length"][i], 4),
        "correctness": round(scores["correctness"][i], 4),
        "language": round(scores["language"][i], 4),
        "weighted_total": weighted_total[i],
    }
    report["cases"].append(row)
    print(
        f"{c['name']:26s} | {row['format']:6.2f} | {row['reasoning_length']:6.2f} | "
        f"{row['correctness']:7.3f} | {row['language']:5.2f} | {row['weighted_total']:7.3f}"
    )

# ==================== Assertion sanity ====================
f = scores["format"]
lng = scores["reasoning_length"]
corr = scores["correctness"]
lang = scores["language"]
checks = {
    "format A=1": f[0] == 1.0,
    "format B=0 (no tag)": f[1] == 0.0,
    "format conversational E=1": f[4] == 1.0,
    "length A > length C (300 > pendek)": lng[0] > lng[2],
    "length A > length D (300 > kepanjangan)": lng[0] > lng[3],
    "length B == 0 (no think)": lng[1] == 0.0,
    "correctness A >= correctness B (ID match > EN)": corr[0] >= corr[1],
    "language A == 1 (ID)": lang[0] == 1.0,
    "language B == -0.5 (EN penalty)": lang[1] == R.LANG_PENALTY_VALUE,
    "parsing A == E (string vs conversational)": abs(weighted_total[0] - weighted_total[4]) < 1e-9,
}
report["checks"] = checks
print("\nSanity checks:")
all_ok = True
for name, ok in checks.items():
    all_ok = all_ok and ok
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

out_dir = os.path.join(ROOT, "outputs", "samples")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "reward_verify.json")
report["all_pass"] = all_ok
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)
print(f"\n{'ALL PASS' if all_ok else 'SOME FAILED'} -> {out_path}")
sys.exit(0 if all_ok else 1)
