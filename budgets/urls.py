from django.urls import path

from budgets.views import BudgetRequestCreateView

urlpatterns = [
    path(
        'studios/<slug:slug>/orcamento/',
        BudgetRequestCreateView.as_view(),
        name='budget-create',
    ),
]
