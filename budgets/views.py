from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View

from budgets.forms import BudgetRequestForm
from budgets.models import BUDGET_STATUS_SENT
from core.constants import CLIENT
from core.mixins import RoleRequiredMixin
from studios.models import Studio


class BudgetRequestCreateView(RoleRequiredMixin, View):
    allowed_roles = (CLIENT,)

    def post(self, request, slug):
        studio = get_object_or_404(Studio, slug=slug, is_active=True)
        form = BudgetRequestForm(
            request.POST,
            request.FILES,
            studio=studio,
        )
        if form.is_valid():
            budget = form.save(commit=False)
            budget.client = request.user
            budget.studio = studio
            budget.status = BUDGET_STATUS_SENT
            budget.save()
            messages.success(request, 'Orçamento enviado com sucesso.')
            return redirect('studio-detail', slug=slug)

        for error in form.errors.values():
            messages.error(request, error.as_text())
        return redirect('studio-detail', slug=slug)
