"""Download de imagens para dados de demonstração e fallbacks estáticos."""

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.base import ContentFile

USER_AGENT = 'InkNation/1.0 (demo seed)'

PICSUM_BASE = 'https://picsum.photos/seed'

# Seeds fixos para capas por estado (fotos variadas, estáveis via picsum).
STUDIO_COVER_SEEDS = {
    'SP': 'inknation-cover-sp',
    'RJ': 'inknation-cover-rj',
    'MG': 'inknation-cover-bh',
    'default': 'inknation-cover-default',
}

STATIC_DEFAULTS = {
    'cover-sp.jpg': ('inknation-cover-sp', 800, 600),
    'cover-rj.jpg': ('inknation-cover-rj', 800, 600),
    'cover-bh.jpg': ('inknation-cover-bh', 800, 600),
    'cover-default.jpg': ('inknation-cover-default', 800, 600),
}

# Paleta escura com destaque vermelho para fallback offline.
FALLBACK_COLORS = [
    (26, 26, 46),
    (22, 33, 62),
    (30, 20, 35),
    (18, 28, 38),
]


def picsum_url(seed: str, width: int, height: int) -> str:
    return f'{PICSUM_BASE}/{seed}/{width}/{height}'


def download_bytes(url: str, timeout: int = 25) -> bytes:
    request = Request(url, headers={'User-Agent': USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def download_image_file(url: str, filename: str) -> ContentFile:
    data = download_bytes(url)
    if len(data) < 1_000:
        raise ValueError(f'Imagem inválida ou muito pequena: {url}')
    return ContentFile(data, name=filename)


def portfolio_url_for(artist_name: str, index: int) -> str:
    digest = hashlib.md5(f'{artist_name}-{index}'.encode()).hexdigest()[:10]
    return picsum_url(f'ink-portfolio-{digest}', 800, 800)


def studio_cover_url_for(state: str) -> str:
    seed = STUDIO_COVER_SEEDS.get(state, STUDIO_COVER_SEEDS['default'])
    return picsum_url(seed, 800, 600)


def fallback_image_file(label: str, index: int = 0) -> ContentFile:
    """Gera JPEG com gradiente quando o download remoto falhar."""
    from PIL import Image, ImageDraw

    color = FALLBACK_COLORS[index % len(FALLBACK_COLORS)]
    accent = (227, 27, 35)
    img = Image.new('RGB', (800, 800), color)
    draw = ImageDraw.Draw(img)
    for y in range(800):
        blend = y / 800
        r = int(color[0] * (1 - blend) + accent[0] * blend * 0.35)
        g = int(color[1] * (1 - blend) + accent[1] * blend * 0.35)
        b = int(color[2] * (1 - blend) + accent[2] * blend * 0.35)
        draw.line([(0, y), (800, y)], fill=(r, g, b))

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    safe_name = hashlib.md5(label.encode()).hexdigest()[:8]
    return ContentFile(buffer.getvalue(), name=f'fallback-{safe_name}.jpg')


def fetch_portfolio_image(artist_name: str, index: int) -> ContentFile:
    url = portfolio_url_for(artist_name, index)
    filename = f'portfolio-{index}.jpg'
    try:
        return download_image_file(url, filename)
    except (URLError, OSError, ValueError):
        return fallback_image_file(f'{artist_name}-{index}', index)


def ensure_static_default_covers(stdout=None) -> None:
    """Baixa capas padrão para static/img/defaults/ se ainda não existirem."""
    static_root = Path(settings.BASE_DIR) / 'static' / 'img' / 'defaults'
    static_root.mkdir(parents=True, exist_ok=True)

    for filename, (seed, width, height) in STATIC_DEFAULTS.items():
        target = static_root / filename
        if target.exists() and target.stat().st_size > 10_000:
            continue
        url = picsum_url(seed, width, height)
        try:
            data = download_bytes(url)
            if len(data) < 1_000:
                raise ValueError('resposta muito pequena')
            target.write_bytes(data)
            if stdout:
                stdout.write(f'  Capa estática salva: {filename}')
        except (URLError, OSError, ValueError) as exc:
            fallback = fallback_image_file(seed, 0)
            target.write_bytes(fallback.read())
            if stdout:
                stdout.write(
                    f'  Capa estática gerada localmente ({filename}): {exc}',
                )


def is_placeholder_image(image_field) -> bool:
    """Detecta placeholders cinza pequenos gerados pelo seed antigo."""
    if not image_field:
        return True
    try:
        if image_field.size < 5_000:
            return True
        image_field.open('rb')
        from PIL import Image

        with Image.open(image_field) as img:
            width, height = img.size
        image_field.close()
        return width <= 200 and height <= 200
    except (OSError, ValueError):
        return False
