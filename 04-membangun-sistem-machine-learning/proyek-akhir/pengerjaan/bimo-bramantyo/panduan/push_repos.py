"""Helper push 2 repository GitHub (Kriteria 1 & 3) ke akun Bimo + isi .txt + regen zip.

PRASYARAT:
  1. `gh` sudah login sebagai akun GitHub Bimo:  gh auth login
  2. Jalankan dari folder `bimo-bramantyo/`:      python panduan/push_repos.py <username_github_bimo>

Yang dilakukan:
  - Menyalin folder repo ke lokasi sementara (agar monorepo tidak terkena .git bersarang),
    git init + commit, lalu `gh repo create --public --source=. --push`.
  - Mengganti placeholder <USERNAME_GITHUB_BIMO> pada kedua file .txt (root & submission).
  - Membangun ulang zip submission.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # folder bimo-bramantyo/

REPOS = [
    {
        "folder": "Eksperimen_SML_Bimo-Bramantyo",
        "nama_repo": "Eksperimen_SML_Bimo-Bramantyo",
        "pesan": "Kriteria 1: eksperimen & preprocessing Wine recognition",
    },
    {
        "folder": "Workflow-CI",
        "nama_repo": "Workflow-CI",
        "pesan": "Kriteria 3: MLflow Project + GitHub Actions CI",
    },
]


def jalankan(cmd, cwd=None):
    print(f"  $ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def push_repo(username: str, repo: dict):
    sumber = ROOT / repo["folder"]
    if not sumber.is_dir():
        raise SystemExit(f"Folder tidak ditemukan: {sumber}")

    with tempfile.TemporaryDirectory() as tmp:
        tujuan = Path(tmp) / repo["folder"]
        shutil.copytree(
            sumber, tujuan,
            ignore=shutil.ignore_patterns(
                "mlruns", "__pycache__", ".git", "*.pyc", ".ipynb_checkpoints"),
        )
        print(f"\n=== Push {repo['nama_repo']} ===")
        jalankan(["git", "init", "-b", "main"], cwd=tujuan)
        jalankan(["git", "add", "-A"], cwd=tujuan)
        jalankan(["git", "commit", "-m", repo["pesan"]], cwd=tujuan)
        jalankan(
            ["gh", "repo", "create", repo["nama_repo"],
             "--public", "--source=.", "--push", "--remote=origin"],
            cwd=tujuan,
        )
    print(f"  -> https://github.com/{username}/{repo['nama_repo']} (PUBLIC)")


def isi_txt(username: str):
    target = [
        ROOT / "Eksperimen_SML_Bimo-Bramantyo.txt",
        ROOT / "Workflow-CI.txt",
        ROOT / "submission" / "SMSML_Bimo-Bramantyo" / "Eksperimen_SML_Bimo-Bramantyo.txt",
        ROOT / "submission" / "SMSML_Bimo-Bramantyo" / "Workflow-CI.txt",
    ]
    for t in target:
        if t.exists():
            teks = t.read_text(encoding="utf-8").replace("<USERNAME_GITHUB_BIMO>", username)
            t.write_text(teks, encoding="utf-8")
            print(f"  isi link: {t.relative_to(ROOT)}")


def build_zip():
    base = ROOT / "submission" / "SMSML_Bimo-Bramantyo"
    zip_path = ROOT / "submission" / "SMSML_Bimo-Bramantyo"
    if base.is_dir():
        if (ROOT / "submission" / "SMSML_Bimo-Bramantyo.zip").exists():
            (ROOT / "submission" / "SMSML_Bimo-Bramantyo.zip").unlink()
        shutil.make_archive(str(zip_path), "zip", root_dir=base.parent, base_dir=base.name)
        print(f"  zip: {zip_path}.zip")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Pemakaian: python panduan/push_repos.py <username_github_bimo>")
    username = sys.argv[1].strip()
    for repo in REPOS:
        push_repo(username, repo)
    print("\n=== Isi file .txt dengan URL asli ===")
    isi_txt(username)
    print("\n=== Regenerate zip submission ===")
    build_zip()
    print("\nSELESAI. Cek tab Actions repo Workflow-CI sampai run hijau, lalu upload zip ke Dicoding.")


if __name__ == "__main__":
    main()
