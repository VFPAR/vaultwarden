#!/usr/bin/env python3
"""Gera todas as imagens da marca PAR Participações a partir de branding/source/.

Uso (na raiz do repositório):  python branding/generate.py
Requer Pillow (pip install pillow).

Saídas:
  - src/static/images/*          -> imagens embutidas no binário (e-mails, painel admin, 404)
  - branding/web-vault/**        -> arquivos sobrepostos ao web vault durante o build Docker
"""

import base64
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "branding" / "source"
STATIC = ROOT / "src" / "static" / "images"
WEB_VAULT = ROOT / "branding" / "web-vault"

BRAND_BLUE = (29, 70, 155)  # #1D469B


def load(name):
    im = Image.open(SOURCE / name).convert("RGBA")
    return im.crop(im.getchannel("A").getbbox())


def to_height(im, height):
    return im.resize((round(im.width * height / im.height), height), Image.LANCZOS)


def square(im, size):
    return im.resize((size, size), Image.LANCZOS)


def white_only(im):
    """Mantém apenas os elementos brancos da arte, com fundo transparente."""
    out = Image.new("RGBA", im.size)
    src, dst = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            _, g, _, a = src[x, y]
            t = max(0.0, min(1.0, (g - BRAND_BLUE[1]) / (255 - BRAND_BLUE[1])))
            dst[x, y] = (255, 255, 255, round(t * a))
    return out


def recolor(im, rgb):
    """Pinta os elementos de uma arte branca/transparente com a cor informada."""
    out = Image.new("RGBA", im.size, rgb + (0,))
    out.putalpha(im.getchannel("A"))
    return out


def on_canvas(im, size, align="left"):
    fitted = im.copy()
    fitted.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGBA", size)
    x = 0 if align == "left" else (size[0] - fitted.width) // 2
    canvas.alpha_composite(fitted, (x, (size[1] - fitted.height) // 2))
    return canvas


def svg_wrapper(im, view_box):
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    w, h = view_box
    return (
        f'<svg version="1.1" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink"><title>PAR Participações</title>'
        f'<image width="{w}" height="{h}" xlink:href="data:image/png;base64,{data}"/></svg>\n'
    )


def save(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True)


def page_404():
    im = Image.new("LA", (500, 222), (0, 0))
    draw = ImageDraw.Draw(im)
    try:
        big = ImageFont.truetype("segoeuil.ttf", 130)
        small = ImageFont.truetype("segoeui.ttf", 26)
    except OSError:
        big = ImageFont.truetype("DejaVuSans.ttf", 120)
        small = ImageFont.truetype("DejaVuSans.ttf", 24)
    draw.text((250, 85), "404", font=big, fill=(80, 255), anchor="mm")
    draw.text((250, 190), "Voltar para o VF Guard?", font=small, fill=(80, 255), anchor="mm")
    return im


def main():
    logo = load("par-logo.png")
    icon = load("par-icon.png")
    logo_white = white_only(logo)
    icon_white = white_only(icon)
    # Apenas o símbolo, sem o fundo azul, para ícones pequenos sobre fundo claro
    icon_mark = recolor(icon_white.crop(icon_white.getchannel("A").getbbox()), BRAND_BLUE)
    icon_white_mark = icon_white.crop(icon_white.getchannel("A").getbbox())

    # Imagens embutidas no servidor
    save(to_height(logo, 132), STATIC / "logo-gray.png")
    save(to_height(logo_white, 132), STATIC / "logo-white.png")
    save(on_canvas(icon_white_mark, (64, 64), "center"), STATIC / "par-icon-white.png")
    save(square(icon, 64), STATIC / "vaultwarden-icon.png")
    save(square(icon, 32), STATIC / "vaultwarden-favicon.png")
    save(page_404(), STATIC / "404.png")

    # Sobreposição do web vault
    for folder in (WEB_VAULT / "images", WEB_VAULT / "images" / "icons"):
        for size, name in (
            (16, "favicon-16x16.png"),
            (32, "favicon-32x32.png"),
            (180, "apple-touch-icon.png"),
            (192, "android-chrome-192x192.png"),
            (512, "android-chrome-512x512.png"),
            (270, "mstile-150x150.png"),
        ):
            save(square(icon, size), folder / name)
    save(on_canvas(icon_mark, (32, 32), "center"), WEB_VAULT / "images" / "icon-dark.png")
    save(on_canvas(icon_white_mark, (32, 32), "center"), WEB_VAULT / "images" / "icon-white.png")
    save(on_canvas(logo, (568, 86)), WEB_VAULT / "images" / "logo-dark@2x.png")
    save(on_canvas(logo_white, (568, 86)), WEB_VAULT / "images" / "logo-white@2x.png")
    (WEB_VAULT / "images" / "logo.svg").write_text(svg_wrapper(on_canvas(logo, (580, 120)), (290, 60)), encoding="utf-8")
    (WEB_VAULT / "images" / "logo-white.svg").write_text(
        svg_wrapper(on_canvas(logo_white, (580, 120)), (290, 60)), encoding="utf-8"
    )
    (WEB_VAULT / "images" / "icon-white.svg").write_text(
        svg_wrapper(on_canvas(icon_white_mark, (128, 128), "center"), (32, 32)), encoding="utf-8"
    )
    square(icon, 48).save(WEB_VAULT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    print("Imagens geradas com sucesso.")


if __name__ == "__main__":
    main()
