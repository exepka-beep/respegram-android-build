#!/usr/bin/env python3
"""Перерисовать все иконки overlay под стандартное лого Telegram."""
import os
import sys
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "files/TMessagesProj/src/main/res"
SRC = Path(r"E:/xtreegram-build/android/TMessagesProj/src/main/res/drawable-nodpi/server_telegram.png")
BLUE = (41, 169, 239, 255)


def make_plane(src):
    r, g, b, _ = src.split()
    minc = ImageChops.darker(ImageChops.darker(r, g), b)
    mask = minc.point(lambda v: 0 if v <= 70 else min(255, int((v - 70) * 255 / 120)))
    plane = Image.new("RGBA", src.size, (255, 255, 255, 0))
    plane.putalpha(mask)
    box = mask.getbbox() or (0, 0, src.width, src.height)
    return plane.crop(box)


def main():
    src = Image.open(SRC).convert("RGBA")
    plane = make_plane(src)
    n = 0

    for p in RES.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in (".png", ".webp"):
            continue
        name = p.name.lower()
        try:
            w, h = Image.open(p).size
        except Exception:
            continue
        side = max(w, h)

        if "background" in name:
            img = Image.new("RGBA", (side, side), BLUE)
        elif "foreground" in name:
            target = int(side * 0.62)
            ratio = min(target / plane.width, target / plane.height)
            scaled = plane.resize((max(1, int(plane.width * ratio)), max(1, int(plane.height * ratio))), Image.LANCZOS)
            img = Image.new("RGBA", (side, side), (255, 255, 255, 0))
            img.alpha_composite(scaled, ((side - scaled.width) // 2, (side - scaled.height) // 2))
        else:
            img = src.resize((side, side), Image.LANCZOS)

        tmp = p.with_name(p.name + ".new")
        if p.suffix.lower() == ".webp":
            img.save(tmp, "WEBP", quality=95, method=6)
        else:
            img.save(tmp, "PNG")
        os.replace(tmp, p)
        n += 1

    # тот же логотип на сплэше/интро/в списке серверов
    logo = ROOT / "files/TMessagesProj/src/main/res/drawable-nodpi/server_owpengram.png"
    if logo.parent.exists():
        src.resize((1024, 1024), Image.LANCZOS).save(logo)
    print("icons:", n)


if __name__ == "__main__":
    main()
