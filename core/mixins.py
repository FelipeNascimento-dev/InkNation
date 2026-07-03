from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404

from core.constants import SYSTEM_ADMIN
from core.utils.studio_access import user_can_manage_studio, user_is_studio_owner


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in self.allowed_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SystemAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        is_admin = request.user.is_superuser or request.user.role == SYSTEM_ADMIN
        if not is_admin:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class _StudioScopedMixin(LoginRequiredMixin):
    """Resolve estúdio por slug ou id/pk na URL e valida acesso."""

    studio_url_kwarg = 'slug'
    studio_id_kwarg = 'id'

    def get_studio(self):
        if hasattr(self, '_ink_studio'):
            return self._ink_studio

        Studio = apps.get_model('studios', 'Studio')
        kwargs = self.kwargs

        if self.studio_url_kwarg in kwargs:
            lookup = {self.studio_url_kwarg: kwargs[self.studio_url_kwarg]}
        elif self.studio_id_kwarg in kwargs:
            lookup = {'pk': kwargs[self.studio_id_kwarg]}
        elif 'pk' in kwargs:
            lookup = {'pk': kwargs['pk']}
        else:
            raise Http404

        try:
            self._ink_studio = Studio.objects.get(**lookup)
        except Studio.DoesNotExist:
            raise Http404
        return self._ink_studio

    def _user_has_studio_access(self, user, studio):
        raise NotImplementedError

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        studio = self.get_studio()
        if not self._user_has_studio_access(request.user, studio):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class StudioOwnerRequiredMixin(_StudioScopedMixin):
    def _user_has_studio_access(self, user, studio):
        return user_is_studio_owner(user, studio)


class StudioStaffOrOwnerMixin(_StudioScopedMixin):
    def _user_has_studio_access(self, user, studio):
        return user_can_manage_studio(user, studio)
