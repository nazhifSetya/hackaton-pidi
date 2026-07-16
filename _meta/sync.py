#!/usr/bin/env python3
"""
Helper sync lintas-device untuk repo Hackaton PIDI.
Jalan SAMA di Mac (zsh) & Victus (Windows/PowerShell) — cuma butuh Python 3 + git.
Ini OPSIONAL: semua yang dilakukan di sini bisa juga diketik manual (lihat /CLAUDE.md).

Pakai:
    python _meta/sync.py start           # git pull --rebase --autostash + tampilkan handoff
    python _meta/sync.py status          # status git (ahead/behind) + ringkas STATUS.md
    python _meta/sync.py end "pesan"     # git add -A + commit + push (konfirmasi dulu)

Kenapa pakai Python, bukan .sh / .ps1? Supaya SATU file jalan di dua device tanpa
pusing beda shell (zsh vs PowerShell, `&&` yang nggak jalan di PowerShell lama).
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # root repo = induk folder _meta/
STATUS = REPO / "_meta" / "STATUS.md"
H_START, H_END = "<!-- HANDOFF:START -->", "<!-- HANDOFF:END -->"


def git(*args, check=True, capture=False):
    """Jalankan git di root repo. cwd=REPO biar aman dipanggil dari folder mana pun."""
    print(f"  $ git {' '.join(args)}")
    r = subprocess.run(
        ["git", *args], cwd=REPO,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    if check and r.returncode != 0:
        sys.exit(f"\n[X] git {' '.join(args)} gagal (exit {r.returncode}). Berhenti — cek manual.")
    return (r.stdout or "") if capture else ""


def print_handoff():
    """Tampilkan bagian FOKUS SAAT INI / HANDOFF dari STATUS.md."""
    if not STATUS.exists():
        print("  (belum ada _meta/STATUS.md)")
        return
    text = STATUS.read_text(encoding="utf-8", errors="replace")
    if H_START in text and H_END in text:
        block = text.split(H_START, 1)[1].split(H_END, 1)[0].strip()
    else:
        block = "\n".join(text.splitlines()[:40])  # fallback: 40 baris pertama
    print("\n" + "=" * 70)
    print("FOKUS SAAT INI / HANDOFF (dari _meta/STATUS.md)")
    print("=" * 70)
    print(block)
    print("=" * 70)


def ahead_behind():
    out = git("rev-list", "--left-right", "--count", "HEAD...@{u}", check=False, capture=True).strip()
    if out and "\t" in out:
        ahead, behind = out.split("\t")
        print(f"  Local ahead {ahead} / behind {behind} vs remote.")


def cmd_start():
    print("\n== SYNC START ==")
    git("fetch", "--all", "--quiet", check=False)
    git("pull", "--rebase", "--autostash")
    print_handoff()
    print("\n[OK] Repo up-to-date. Baca handoff di atas, lalu mulai kerja.\n")


def cmd_status():
    print("\n== STATUS ==")
    git("status", "-sb", check=False)
    ahead_behind()
    print_handoff()


def cmd_end(message):
    print("\n== SYNC END ==")
    git("add", "-A")
    changes = git("status", "--short", check=False, capture=True).strip()
    if not changes:
        print("  Tidak ada perubahan untuk di-commit. Selesai.")
        return
    print("\n  Perubahan yang akan di-commit:")
    print("\n".join("    " + ln for ln in changes.splitlines()))
    print("\n  PENGINGAT: sudah update _meta/STATUS.md (handoff + stempel tanggal)? "
          "Sudah pastikan tak ada token/rahasia?")
    if input('\n  Ketik "ya" untuk commit + push: ').strip().lower() not in ("ya", "y", "yes"):
        sys.exit("  Dibatalkan. Perubahan tetap ter-`git add` (belum commit).")
    git("commit", "-m", message)
    git("push")
    print("\n[OK] Ter-push ke remote. Aman pindah device.\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("start", "status", "end"):
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "start":
        cmd_start()
    elif cmd == "status":
        cmd_status()
    elif cmd == "end":
        if len(sys.argv) < 3:
            sys.exit('  Butuh pesan commit. Contoh:\n    python _meta/sync.py end "sync(03/nazhif): fix RAG reranker [device: mac]"')
        cmd_end(sys.argv[2])


if __name__ == "__main__":
    main()
