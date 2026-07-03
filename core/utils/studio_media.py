"""Resolução de URLs de capa para estúdios."""

from django.core.files.storage import default_storage
from django.templatetags.static import static

DEFAULT_COVERS_BY_STATE = {
    'SP': 'img/defaults/cover-sp.jpg',
    'RJ': 'img/defaults/cover-rj.jpg',
    'MG': 'img/defaults/cover-bh.jpg',
}
DEFAULT_COVER = 'img/defaults/cover-default.jpg'


def resolve_studio_cover_url(cover_image_path=None, state=None) -> str:
    if cover_image_path:
        return default_storage.url(cover_image_path)
    rel_path = DEFAULT_COVERS_BY_STATE.get(state, DEFAULT_COVER)
    return static(rel_path)


def resolve_studio_cover_absolute(request, cover_image_path=None, state=None) -> str:
    return request.build_absolute_uri(
        resolve_studio_cover_url(cover_image_path, state),
    )


def cover_image_path_for_studio(studio) -> str | None:
    """Primeira imagem de portfólio do estúdio, se houver."""
    for artist in studio.artists.all():
        for item in artist.portfolio_items.all():
            if item.image:
                return item.image.name
    return None


def resolve_studio_cover_for_instance(studio) -> str:
    return resolve_studio_cover_url(
        cover_image_path_for_studio(studio),
        studio.state,
    )
