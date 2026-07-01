from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404

from studios.models import Studio


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
        is_admin = (
            request.user.is_superuser
            or request.user.groups.filter(name='SYSTEM_ADMIN').exists()
        )
        if not is_admin:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class StudioAccessMixin(LoginRequiredMixin):
    studio_url_kwarg = 'slug'

    def get_studio(self):
        if not hasattr(self.request, '_ink_studio'):
            slug = self.kwargs[self.studio_url_kwarg]
            self.request._ink_studio = Studio.objects.get(slug=slug)
        return self.request._ink_studio

    def _user_has_studio_access(self, user, studio):
        return (
            studio.owners.filter(pk=user.pk).exists()
            or studio.staffs.filter(pk=user.pk).exists()
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            studio = self.get_studio()
        except Studio.DoesNotExist:
            raise Http404
        if not self._user_has_studio_access(request.user, studio):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class StudioOwnerRequiredMixin(StudioAccessMixin):
    def _user_has_studio_access(self, user, studio):
        return user.role == 'owner' and studio.owners.filter(pk=user.pk).exists()


class StudioOwnerOrStaffRequiredMixin(StudioAccessMixin):
    def _user_has_studio_access(self, user, studio):
        if user.role not in ('owner', 'staff'):
            return False
        return (
            studio.owners.filter(pk=user.pk).exists()
            or studio.staffs.filter(pk=user.pk).exists()
        )
