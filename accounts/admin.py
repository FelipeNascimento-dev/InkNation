from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import CustomUser, UsernameSequence


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'cpf', 'role', 'phone', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'cpf', 'phone')
    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        ('InkNation', {'fields': ('cpf', 'phone', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'cpf', 'phone', 'role'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly.append('role')
            readonly.append('is_superuser')
            readonly.append('is_staff')
        return readonly


@admin.register(UsernameSequence)
class UsernameSequenceAdmin(admin.ModelAdmin):
    list_display = ('last_number',)

    def has_add_permission(self, request):
        return not UsernameSequence.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
