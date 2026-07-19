"""
Generator ikon RootFacts (versi Dafina) — motif DAUN.
Sengaja dibedakan dari ikon anggota lain (sprout / wortel) untuk anti-plagiarisme,
tetap bertema hijau sayuran. Menghasilkan 4 berkas di assets/icons/:
  icon-192x192.png, icon-512x512.png, apple-touch-icon.png, favicon.ico
Full-bleed (background hijau menutup seluruh kanvas) sehingga aman untuk maskable.
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "submission" / "root-facts" / "assets" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

GREEN = (21, 128, 61, 255)     # #15803d — hijau daun (aksen khas Dafina)
WHITE = (255, 255, 255, 255)

def render(size: int) -> Image.Image:
    S = 512  # gambar di resolusi master lalu perkecil agar mulus
    img = Image.new("RGBA", (S, S), GREEN)

    # Lapisan daun (vertikal dulu, baru diputar).
    leaf = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(leaf)

    cx, cy = S / 2, S / 2
    w, h = S * 0.40, S * 0.74
    bbox = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    d.ellipse(bbox, fill=WHITE)

    # Tulang daun tengah (midrib).
    rib_w = int(S * 0.022)
    d.line([(cx, cy - h / 2 + S * 0.02), (cx, cy + h / 2 - S * 0.02)], fill=GREEN, width=rib_w)

    # Urat samping berpasangan, menyerong ke atas.
    vein_w = int(S * 0.014)
    for frac in (0.24, 0.46, 0.68):
        y = cy - h / 2 + h * frac
        span = w * (0.42 - frac * 0.28)
        lift = h * 0.10
        d.line([(cx, y), (cx - span, y - lift)], fill=GREEN, width=vein_w)
        d.line([(cx, y), (cx + span, y - lift)], fill=GREEN, width=vein_w)

    leaf = leaf.rotate(-35, resample=Image.BICUBIC, center=(cx, cy))
    img.alpha_composite(leaf)

    # Tangkai daun (putih) dari pangkal bawah.
    d2 = ImageDraw.Draw(img)
    d2.line([(cx + S * 0.16, cy + S * 0.22), (cx + S * 0.26, cy + S * 0.34)],
            fill=WHITE, width=int(S * 0.03))

    if size != S:
        img = img.resize((size, size), Image.LANCZOS)
    return img

# PNG utama
render(192).save(OUT / "icon-192x192.png")
render(512).save(OUT / "icon-512x512.png")
render(180).save(OUT / "apple-touch-icon.png")

# Favicon multi-ukuran
ico = render(64)
ico.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

print("Ikon daun tersimpan di:", OUT)
for p in sorted(OUT.glob("*")):
    print(" -", p.name, p.stat().st_size, "bytes")
