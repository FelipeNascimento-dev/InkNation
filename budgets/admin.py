from django.contrib import admin

from budgets.models import BudgetRequest


@admin.register(BudgetRequest)
class BudgetRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'studio', 'artist', 'status', 'created_at')
    list_filter = ('status', 'studio', 'created_at')
    search_fields = ('client__email', 'client__username', 'studio__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('client', 'studio', 'artist')
