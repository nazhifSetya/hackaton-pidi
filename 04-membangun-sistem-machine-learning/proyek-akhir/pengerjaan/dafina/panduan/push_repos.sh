#!/usr/bin/env bash
# Helper: buat 2 repository GitHub PUBLIC (Kriteria 1 & 3) lalu push.
#
# Repo dibuat dari SALINAN sementara supaya monorepo hackaton-pidi tidak
# ketularan .git bersarang. Jalankan dari mana saja.
#
# PRASYARAT:
#   - gh sudah login sebagai akun yang diinginkan:  gh auth status
#     (ganti akun bila perlu:  gh auth login)
#
# PAKAI:  bash push_repos.sh
set -euo pipefail

DAFINA_DIR="d:/Kalachakra/hackaton-pidi/04-membangun-sistem-machine-learning/proyek-akhir/pengerjaan/dafina"
GH_USER="$(gh api user --jq .login)"
echo "Akun GitHub aktif: $GH_USER"
echo ""

push_one() {
  local src="$1" name="$2" desc="$3"
  local tmp; tmp="$(mktemp -d)"
  echo ">> Menyiapkan $name ..."
  cp -r "$src/." "$tmp/"
  ( cd "$tmp"
    rm -rf .venv mlruns **/mlruns __pycache__ .git 2>/dev/null || true
    git init -q -b main
    git add -A
    git -c user.email="dev@kalachakra.io" -c user.name="$GH_USER" commit -qm "init: $name"
    gh repo create "$name" --public --source=. --remote=origin --push \
       --description "$desc"
  )
  rm -rf "$tmp"
  echo "   -> https://github.com/$GH_USER/$name"
  echo ""
}

push_one "$DAFINA_DIR/Eksperimen_SML_Dafina-Meira-Rizkia" \
         "Eksperimen_SML_Dafina-Meira-Rizkia" \
         "Kriteria 1 SMSML — eksperimen & preprocessing Palmer Penguins (Dafina Meira Rizkia)"

push_one "$DAFINA_DIR/Workflow-CI" \
         "Workflow-CI" \
         "Kriteria 3 SMSML — MLflow Project + GitHub Actions retraining (Dafina Meira Rizkia)"

echo "SELESAI. Update kedua file .txt dengan URL di atas (ganti <USERNAME-GITHUB> -> $GH_USER),"
echo "lalu regenerate zip submission."
