"""4 reward function untuk GRPO (K1 Advanced).

Semua fungsi mengikuti signature TRL GRPOTrainer:
`f(prompts, completions, **kwargs) -> list[float]` — panjang list == jumlah
completion. Kolom dataset (mis. `ground_truth`) diterima sebagai kwargs oleh
GRPOTrainer. Bobot antar-reward di-apply oleh `GRPOConfig.reward_weights`,
jadi tiap fungsi mengembalikan skor MENTAH (belum dikali bobot).

Tunable mirror `configs/grpo_config.yaml`. Library eksternal (rouge_score,
langdetect) dipakai kalau tersedia; kalau tidak, ada fallback pure-Python
supaya modul tetap jalan + bisa di-verify tanpa GPU/paket berat.
"""

import re
import math

# ==================== Tunables (mirror configs/grpo_config.yaml) ====================
THINK_PATTERN = re.compile(r"<think>(.*?)</think>", re.DOTALL)
FORMAT_REWARD_PRESENT = 1.0
FORMAT_REWARD_ABSENT = 0.0

REASONING_PEAK_CHAR = 300
REASONING_SPREAD = 150

LANG_ID_THRESHOLD = 0.7          # id_prob >= 0.7 -> reward penuh 1.0
LANG_EN_PENALTY_THRESHOLD = 0.3  # id_prob < 0.3 -> penalty
LANG_PENALTY_VALUE = -0.5


# ==================== Helper ekstraksi teks ====================
def _completion_text(completion):
    """Ambil teks dari satu completion.

    Support dua format TRL:
      - conversational: [{"role": "assistant", "content": "..."}]
      - standard: "..." (string biasa)
    """
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list) and completion:
        last = completion[-1]
        if isinstance(last, dict):
            return last.get("content", "")
        return str(last)
    if isinstance(completion, dict):
        return completion.get("content", "")
    return str(completion)


def _extract_think(text):
    """Isi di dalam <think>...</think> (kosong kalau tag tak ada)."""
    m = THINK_PATTERN.search(text)
    return m.group(1).strip() if m else ""


def _extract_answer(text):
    """Jawaban final = teks setelah </think>. Tanpa tag -> seluruh teks."""
    if "</think>" in text:
        return text.split("</think>", 1)[1].strip()
    return text.strip()


# ==================== 1. format_reward_func ====================
def format_reward_func(prompts=None, completions=None, **kwargs):
    """1.0 kalau ada blok <think>...</think>, else 0.0."""
    texts = [_completion_text(c) for c in completions]
    return [
        FORMAT_REWARD_PRESENT if THINK_PATTERN.search(t) else FORMAT_REWARD_ABSENT
        for t in texts
    ]


# ==================== 2. reasoning_length_reward ====================
def reasoning_length_reward(prompts=None, completions=None, **kwargs):
    """Kurva lonceng halus terhadap panjang reasoning, puncak di PEAK_CHAR.

    r = 1 / (1 + ((len - peak) / spread)^2). Reasoning kosong -> 0.0.
    """
    texts = [_completion_text(c) for c in completions]
    rewards = []
    for t in texts:
        think = _extract_think(t)
        if not think:
            rewards.append(0.0)
            continue
        length = len(think)
        r = 1.0 / (1.0 + ((length - REASONING_PEAK_CHAR) / REASONING_SPREAD) ** 2)
        rewards.append(float(r))
    return rewards


# ==================== 3. correctness_reward (ROUGE-L) ====================
try:
    from rouge_score import rouge_scorer as _rs

    _SCORER = _rs.RougeScorer(["rougeL"], use_stemmer=False)

    def _rouge_l(pred, ref):
        if not pred or not ref:
            return 0.0
        return float(_SCORER.score(ref, pred)["rougeL"].fmeasure)

    _ROUGE_BACKEND = "rouge_score"
except Exception:  # fallback pure-Python LCS-based ROUGE-L

    def _lcs_len(a, b):
        m, n = len(a), len(b)
        prev = [0] * (n + 1)
        for i in range(1, m + 1):
            cur = [0] * (n + 1)
            ai = a[i - 1]
            for j in range(1, n + 1):
                cur[j] = prev[j - 1] + 1 if ai == b[j - 1] else max(prev[j], cur[j - 1])
            prev = cur
        return prev[n]

    def _rouge_l(pred, ref):
        p, r = pred.split(), ref.split()
        if not p or not r:
            return 0.0
        lcs = _lcs_len(p, r)
        if lcs == 0:
            return 0.0
        prec, rec = lcs / len(p), lcs / len(r)
        return float(2 * prec * rec / (prec + rec))

    _ROUGE_BACKEND = "fallback_lcs"


def correctness_reward(prompts=None, completions=None, ground_truth=None, **kwargs):
    """ROUGE-L f-measure antara jawaban final (setelah </think>) vs ground_truth."""
    texts = [_completion_text(c) for c in completions]
    if ground_truth is None:
        ground_truth = [""] * len(texts)
    rewards = []
    for t, gt in zip(texts, ground_truth):
        ans = _extract_answer(t).lower()
        rewards.append(_rouge_l(ans, (gt or "").lower()))
    return rewards


# ==================== 4. language_reward_func ====================
try:
    from langdetect import detect_langs, DetectorFactory

    DetectorFactory.seed = 42

    def _id_prob(text):
        if not text.strip():
            return 0.0
        try:
            return {l.lang: l.prob for l in detect_langs(text)}.get("id", 0.0)
        except Exception:
            return 0.0

    _LANG_BACKEND = "langdetect"
except Exception:  # fallback rasio stopword ID vs EN
    _ID_STOP = {
        "yang", "dan", "di", "ke", "dari", "untuk", "adalah", "dengan", "pada",
        "tidak", "ini", "itu", "atau", "dalam", "akan", "karena", "sebagai",
        "oleh", "juga", "dapat", "harus", "sebagaimana", "dimaksud", "ayat", "pasal",
    }
    _EN_STOP = {
        "the", "and", "of", "to", "in", "is", "that", "for", "with", "as", "are",
        "this", "be", "or", "by", "an", "it", "not", "on", "from", "which", "shall",
    }

    def _id_prob(text):
        words = re.findall(r"[a-zA-Z]+", text.lower())
        if not words:
            return 0.0
        idc = sum(w in _ID_STOP for w in words)
        enc = sum(w in _EN_STOP for w in words)
        tot = idc + enc
        if tot == 0:
            return 0.5  # netral (tak ada penanda kuat)
        return idc / tot

    _LANG_BACKEND = "fallback_stopword"


def language_reward_func(prompts=None, completions=None, **kwargs):
    """Reward Bahasa Indonesia, penalty kalau dominan non-ID (Inggris)."""
    texts = [_completion_text(c) for c in completions]
    rewards = []
    for t in texts:
        ans = _extract_answer(t) or t
        p = _id_prob(ans)
        if p >= LANG_ID_THRESHOLD:
            rewards.append(1.0)
        elif p < LANG_EN_PENALTY_THRESHOLD:
            rewards.append(LANG_PENALTY_VALUE)
        else:
            rewards.append(float(p))
    return rewards


# ==================== Registry (urutan == urutan reward_weights) ====================
REWARD_FUNCS = [
    format_reward_func,
    reasoning_length_reward,
    correctness_reward,
    language_reward_func,
]
REWARD_WEIGHTS = [0.30, 0.15, 0.40, 0.15]

BACKENDS = {"rouge": _ROUGE_BACKEND, "language": _LANG_BACKEND}
