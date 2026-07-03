from core.utils.studio_access import studios_for_user_navigation


def studio_navigation(request):
    return {
        'nav_studios': studios_for_user_navigation(request.user),
    }
