from django.contrib import admin

from budgets.models import BudgetRequest


@admin.register(BudgetRequest)
class BudgetRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'studio', 'artist', 'status', 'created_at')
    list_filter = ('status', 'studio')
    search_fields = ('client__username', 'client__email', 'studio__name')
    readonly_fields = ('created_at', 'updated_at')
