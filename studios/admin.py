from django.contrib import admin, messages

from studios.models import (
    APPROVAL_STATUS_APPROVED,
    PortfolioItem,
    Studio,
    StudioApprovalRequest,
    TattooArtist,
)


class StudioApprovalRequestInline(admin.StackedInline):
    model = StudioApprovalRequest
    extra = 0
    readonly_fields = ('requested_by', 'created_at', 'updated_at')
    can_delete = False


@admin.action(description='Aprovar estúdio selecionado')
def approve_studio(modeladmin, request, queryset):
    approved = 0
    for studio in queryset:
        studio.is_active = True
        studio.save(update_fields=['is_active', 'updated_at'])
        approval, _ = StudioApprovalRequest.objects.get_or_create(
            studio=studio,
            defaults={'requested_by': studio.owners.first(), 'status': 'pending'},
        )
        if approval.status != APPROVAL_STATUS_APPROVED:
            approval.status = APPROVAL_STATUS_APPROVED
            approval.save(update_fields=['status', 'updated_at'])
        approved += 1
    modeladmin.message_user(
        request,
        f'{approved} estúdio(s) aprovado(s).',
        messages.SUCCESS,
    )


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'is_active', 'created_at')
    list_filter = ('is_active', 'state', 'city')
    search_fields = ('name', 'cnpj', 'slug', 'city')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('owners', 'staffs')
    inlines = [StudioApprovalRequestInline]
    actions = [approve_studio]


@admin.register(StudioApprovalRequest)
class StudioApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('studio', 'requested_by', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('studio__name', 'requested_by__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TattooArtist)
class TattooArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'studio', 'created_at')
    list_filter = ('studio',)
    search_fields = ('name', 'studio__name')


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('artist', 'created_at')
    list_filter = ('artist__studio',)
    search_fields = ('artist__name',)
