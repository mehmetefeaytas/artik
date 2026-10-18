"""Analiz sonucunu görüntü üzerine çizen yardımcı (maske + etiket)."""

from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PALETTE = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#008080", "#f032e6", "#800000", "#469990", "#9a6324",
]

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
]


def _font(size: int = 18) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def color_for(key: str, order: list[str]) -> tuple[int, int, int]:
    idx = order.index(key) % len(PALETTE) if key in order else len(PALETTE) - 1
    hexv = PALETTE[idx].lstrip("#")
    return tuple(int(hexv[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def annotate(
    image: Image.Image,
    segments,
    order: list[str],
    title: str,
    subtitle: str = "",
) -> bytes:
    """Segment maskelerini yarı saydam doldur, kontur + etiket çipi ekle."""
    base = image.copy()
    if base.mode != "RGB":
        base = base.convert("RGB")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fnt = _font(max(14, base.width // 48))
    small = _font(max(11, base.width // 64))

    for seg in segments:
        rgb = color_for(seg.key, order)
        mask = seg.mask.astype(np.uint8) * 255
        m = Image.fromarray(mask, mode="L").resize(base.size)
        solid = Image.new("RGBA", base.size, rgb + (96,))
        overlay.paste(solid, (0, 0), m)

        x0, y0, x1, y1 = seg.bbox
        draw.rectangle([x0, y0, x1, y1], outline=rgb + (255,), width=3)

        label = f"{seg.name_tr} %{seg.score * 100:.0f}"
        tw = draw.textlength(label, font=fnt)
        ty = max(0, y0 - 24)
        draw.rectangle([x0, ty, x0 + tw + 10, ty + 22], fill=rgb + (230,))
        draw.text((x0 + 5, ty + 2), label, font=fnt, fill=(255, 255, 255, 255))

    canvas = Image.alpha_composite(base.convert("RGBA"), overlay)
    d2 = ImageDraw.Draw(canvas)

    d2.rectangle([0, 0, canvas.width, 46], fill=(15, 23, 42, 210))
    d2.text((12, 8), title, font=_font(max(16, canvas.width // 42)), fill=(255, 255, 255))
    if subtitle:
        d2.text((12, 26), subtitle, font=small, fill=(203, 213, 225))
    out = io.BytesIO()
    canvas.convert("RGB").save(out, format="PNG")
    return out.getvalue()
