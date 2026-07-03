from django.urls import path

from budgets.views import BudgetRequestCreateView, BudgetStatusUpdateView

urlpatterns = [
    path(
        'studios/<slug:slug>/orcamento/',
        BudgetRequestCreateView.as_view(),
        name='budget-create',
    ),
    path(
        'studios/<slug:slug>/orcamentos/<uuid:budget_id>/status/',
        BudgetStatusUpdateView.as_view(),
        name='budget-status-update',
    ),
]
