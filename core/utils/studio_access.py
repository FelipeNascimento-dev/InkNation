"""Regras de acesso a estúdios (visualização, gestão e orçamento)."""

from core.constants import CLIENT, STUDIO_OWNER, STUDIO_STAFF


def user_is_studio_owner(user, studio) -> bool:
    return (
        user.is_authenticated
        and user.role == STUDIO_OWNER
        and studio.owners.filter(pk=user.pk).exists()
    )


def user_is_studio_staff(user, studio) -> bool:
    return (
        user.is_authenticated
        and user.role == STUDIO_STAFF
        and studio.staffs.filter(pk=user.pk).exists()
    )


def user_can_manage_studio(user, studio) -> bool:
    return user_is_studio_owner(user, studio) or user_is_studio_staff(user, studio)


def user_can_view_studio(user, studio) -> bool:
    if studio.is_active:
        return True
    return user_can_manage_studio(user, studio)


def user_can_request_budget(user, studio) -> bool:
    return (
        user.is_authenticated
        and user.role == CLIENT
        and studio.is_active
    )


def studios_for_user_navigation(user, limit=5):
    """Estúdios do usuário para links rápidos na navegação."""
    if not user.is_authenticated:
        return []
    if user.role == STUDIO_OWNER:
        return list(user.owned_studios.order_by('name')[:limit])
    if user.role == STUDIO_STAFF:
        return list(user.assigned_studios.filter(is_active=True).order_by('name')[:limit])
    return []
