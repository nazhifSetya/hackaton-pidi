"""Generate ikon RootFacts (motif wortel) untuk submission Fareynaldi.
Background hijau full-bleed (#16a34a, maskable-safe) + wortel oranye dengan
daun hijau muda di atasnya. Sengaja beda dari ikon 'sprout' milik Nazhif."""
from PIL import Image, ImageDraw

GREEN_BG = (22, 163, 74)      # #16a34a
CARROT = (249, 115, 22)       # oranye
CARROT_DARK = (194, 65, 12)   # garis segmen wortel
LEAF = (187, 247, 208)        # hijau muda daun


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), GREEN_BG + (255,))
    d = ImageDraw.Draw(img)
    s = size / 100.0  # skala relatif ke kanvas 100x100

    def P(x, y):
        return (x * s, y * s)

    # --- Badan wortel: segitiga meruncing ke bawah ---
    body = [P(50, 88), P(34, 40), P(66, 40)]
    d.polygon(body, fill=CARROT)

    # Garis-garis segmen wortel (horizontal, makin pendek ke bawah).
    segments = [(40, 44, 60), (43, 54, 57), (46, 64, 54), (48, 74, 52)]
    for xspan_l, y, xspan_r in segments:
        d.line([P(xspan_l, y), P(xspan_r, y)], fill=CARROT_DARK, width=max(1, int(2 * s)))

    # --- Daun: tiga helai di pucuk wortel ---
    d.polygon([P(50, 42), P(44, 18), P(52, 34)], fill=LEAF)   # kiri
    d.polygon([P(50, 42), P(50, 12), P(56, 34)], fill=LEAF)   # tengah
    d.polygon([P(50, 42), P(62, 20), P(56, 36)], fill=LEAF)   # kanan

    return img


def main():
    base = "../submission/root-facts/assets/icons"
    import os
    os.makedirs(base, exist_ok=True)

    icon512 = draw_icon(512)
    icon512.save(f"{base}/icon-512x512.png")
    draw_icon(192).save(f"{base}/icon-192x192.png")
    draw_icon(180).save(f"{base}/apple-touch-icon.png")

    # favicon.ico multi-size
    fav = draw_icon(64)
    fav.save(f"{base}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

    print("Ikon wortel dibuat:", os.listdir(base))


if __name__ == "__main__":
    main()
