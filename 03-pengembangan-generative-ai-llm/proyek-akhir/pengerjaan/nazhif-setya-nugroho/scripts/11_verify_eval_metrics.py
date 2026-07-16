"""
PGABL Tahap 4 - VERIFY-FIRST: retrieval metrics (hit@k/MRR/NDCG) pure-math.
Cek dengan kasus sintetis (nilai bisa dihitung tangan) + parsing ground-truth test-set asli.
"""
from __future__ import annotations
import json, sys, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.eval.retrieval_metrics import (
    norm_pasal, parse_ground_truth, is_relevant, hit_at_k, reciprocal_rank,
    ndcg_at_k, evaluate_queries,
)

def m(pdf, pasal):  # bikin metadata chunk
    return {"pdf_source": pdf, "pasal": pasal}

checks = []

# --- 1. norm_pasal ---
checks.append(("norm_pasal 'Pasal 78'", norm_pasal("Pasal 78"), "78"))
checks.append(("norm_pasal 'pasal  8 '", norm_pasal("pasal  8 "), "8"))

# --- 2. parse_ground_truth cross_pdf ---
gt = parse_ground_truth({"ground_truth_pdf": "UU_6_2023,PP_35_2021",
                         "ground_truth_pasal": "Pasal 78,Pasal 31"})
checks.append(("parse GT cross", gt == {("UU_6_2023", "78"), ("PP_35_2021", "31")}, True))

# --- 3. hit@k / MRR / NDCG kasus tangan ---
# retrieved: [PP35 p1, PP35 p31, PP35 p2, ...], gt = {PP35 p31} -> relevan di posisi 2
ret = [m("PP_35_2021","1"), m("PP_35_2021","31"), m("PP_35_2021","2"), m("PP_5_2021","6"), m("UU_6_2023","78")]
gt1 = {("PP_35_2021","31")}
checks.append(("hit@1 (miss)", hit_at_k(ret, gt1, 1), 0.0))
checks.append(("hit@3 (hit pos2)", hit_at_k(ret, gt1, 3), 1.0))
checks.append(("hit@5", hit_at_k(ret, gt1, 5), 1.0))
checks.append(("MRR (pos2 -> 0.5)", reciprocal_rank(ret, gt1), 0.5))
# NDCG@5: relevan hanya pos2 -> DCG=1/log2(3)=0.6309; IDCG (n_rel=1)=1/log2(2)=1 -> 0.6309
checks.append(("NDCG@5 pos2", round(ndcg_at_k(ret, gt1, 5), 4), round(1/math.log2(3), 4)))

# --- 4. relevan di posisi 1 -> hit@1=1, MRR=1, NDCG=1 ---
ret2 = [m("PP_35_2021","31"), m("PP_35_2021","1")]
checks.append(("hit@1 (pos1)", hit_at_k(ret2, gt1, 1), 1.0))
checks.append(("MRR pos1", reciprocal_rank(ret2, gt1), 1.0))
checks.append(("NDCG@5 pos1", ndcg_at_k(ret2, gt1, 5), 1.0))

# --- 5. cross_pdf: relevan kalau match salah satu pair ---
gt2 = {("UU_6_2023","78"), ("PP_35_2021","31")}
ret3 = [m("PP_5_2021","1"), m("UU_6_2023","78")]  # match pair kedua di pos2
checks.append(("cross hit@3", hit_at_k(ret3, gt2, 3), 1.0))
checks.append(("cross MRR pos2", reciprocal_rank(ret3, gt2), 0.5))

# --- 6. evaluate_queries agregasi ---
rows = [
    {"gt": gt1, "retrieved": ret, "type": "single_pdf", "difficulty": "easy"},   # hit@1=0,hit@3=1,mrr=.5
    {"gt": gt1, "retrieved": ret2, "type": "single_pdf", "difficulty": "hard"},  # hit@1=1,mrr=1
    {"gt": gt2, "retrieved": ret3, "type": "cross_pdf", "difficulty": "hard"},   # hit@1=0,hit@3=1,mrr=.5
]
rep = evaluate_queries(rows)
# overall hit@1 = (0+1+0)/3 = 0.3333 ; mrr = (.5+1+.5)/3 = 0.6667
checks.append(("agg overall hit@1", rep["overall"]["hit@1"], 0.3333))
checks.append(("agg overall mrr", rep["overall"]["mrr"], 0.6667))
checks.append(("agg by_type single hit@1", rep["by_type"]["single_pdf"]["hit@1"], 0.5))
checks.append(("agg by_type cross n", rep["by_type"]["cross_pdf"]["n"], 1))

# --- 7. parse semua ground truth test-set asli (pastikan tak crash + bentuk benar) ---
TS = ROOT / "data" / "test_set" / "legal_qa_testset.jsonl"
rows_ts = [json.loads(l) for l in TS.read_text(encoding="utf-8").splitlines() if l.strip()]
gts = [parse_ground_truth(r) for r in rows_ts]
all_ok = all(isinstance(g, set) and len(g) >= 1 and all(len(p) == 2 for p in g) for g in gts)
checks.append(("parse 45 GT test-set", all_ok, True))
cross_multi = all(len(parse_ground_truth(r)) >= 2 for r in rows_ts if r["type"] == "cross_pdf")
checks.append(("cross_pdf GT >=2 pairs", cross_multi, True))

# --- report ---
n_pass = 0
out = {"checks": []}
for name, got, exp in checks:
    ok = got == exp
    n_pass += ok
    out["checks"].append({"name": name, "got": got, "expected": exp, "pass": ok})
    print(f"  [{'OK ' if ok else 'FAIL'}] {name}: got={got} exp={exp}")
out["passed"] = n_pass
out["total"] = len(checks)
out["sample_ground_truths"] = [sorted(list(g)) for g in gts[:3]] + [sorted(list(gts[-1]))]
SAMPLES = ROOT / "outputs" / "samples"
SAMPLES.mkdir(parents=True, exist_ok=True)
(SAMPLES / "eval_metrics_verify.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n{n_pass}/{len(checks)} checks PASS -> outputs/samples/eval_metrics_verify.json")
