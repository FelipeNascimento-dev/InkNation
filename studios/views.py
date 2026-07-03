from django.contrib import messages
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, TemplateView, View

from budgets.forms import BudgetRequestForm
from budgets.models import BUDGET_STATUS_IN_ANALYSIS, BUDGET_STATUS_SENT, BudgetRequest
from core.constants import CLIENT, STUDIO_OWNER, STUDIO_STAFF
from core.mixins import RoleRequiredMixin, StudioStaffOrOwnerMixin
from studios.forms import PortfolioItemForm, StudioRegistrationForm
from studios.models import Studio, StudioApprovalRequest, TattooArtist


class StudioRegistrationView(RoleRequiredMixin, CreateView):
    model = Studio
    form_class = StudioRegistrationForm
    template_name = 'studios/register.html'
    allowed_roles = (STUDIO_OWNER,)

    def form_valid(self, form):
        with transaction.atomic():
            studio = form.save(commit=False)
            studio.is_active = False
            studio.save()
            studio.owners.add(self.request.user)
            StudioApprovalRequest.objects.create(
                studio=studio,
                requested_by=self.request.user,
                status='pending',
            )
        messages.success(
            self.request,
            'Estúdio cadastrado. Aguarde aprovação do administrador.',
        )
        return redirect('studio-detail', slug=studio.slug)


class StudioDetailView(DetailView):
    model = Studio
    template_name = 'studios/detail.html'
    context_object_name = 'studio'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Studio.objects.prefetch_related(
            'artists__portfolio_items',
            'owners',
            'staffs',
        )

    def get_object(self, queryset=None):
        studio = super().get_object(queryset)
        if studio.is_active:
            return studio
        user = self.request.user
        if user.is_authenticated and (
            studio.owners.filter(pk=user.pk).exists()
            or studio.staffs.filter(pk=user.pk).exists()
        ):
            return studio
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        studio = self.object
        context['can_manage'] = (
            user.is_authenticated
            and (
                studio.owners.filter(pk=user.pk).exists()
                or studio.staffs.filter(pk=user.pk).exists()
            )
        )
        can_request_budget = (
            user.is_authenticated and user.role == CLIENT and studio.is_active
        )
        context['can_request_budget'] = can_request_budget
        if can_request_budget:
            context['budget_form'] = BudgetRequestForm(studio=studio)
        return context


class StudioDashboardView(StudioStaffOrOwnerMixin, TemplateView):
    template_name = 'studios/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        studio = self.get_studio()
        user = self.request.user
        is_owner = (
            user.role == STUDIO_OWNER
            and studio.owners.filter(pk=user.pk).exists()
        )
        is_staff = (
            user.role == STUDIO_STAFF
            and studio.staffs.filter(pk=user.pk).exists()
        )
        budget_qs = BudgetRequest.objects.filter(studio=studio)
        context.update({
            'studio': studio,
            'is_owner': is_owner,
            'is_staff': is_staff,
            'show_operational': is_owner or is_staff,
            'artist_count': studio.artists.count(),
            'budget_count': budget_qs.count(),
            'pending_budgets': budget_qs.filter(
                status__in=(BUDGET_STATUS_SENT, BUDGET_STATUS_IN_ANALYSIS),
            ).count(),
        })
        return context


class PortfolioEditView(StudioStaffOrOwnerMixin, View):
    template_name = 'studios/portfolio_edit.html'

    def get_artist(self, studio):
        return get_object_or_404(
            TattooArtist,
            pk=self.kwargs['artist_id'],
            studio=studio,
        )

    def get(self, request, slug, artist_id):
        studio = self.get_studio()
        artist = self.get_artist(studio)
        return self._render(request, studio, artist, PortfolioItemForm())

    def post(self, request, slug, artist_id):
        studio = self.get_studio()
        artist = self.get_artist(studio)
        form = PortfolioItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.artist = artist
            item.save()
            messages.success(request, 'Item adicionado ao portfólio.')
            return redirect('portfolio-edit', slug=slug, artist_id=artist_id)
        return self._render(request, studio, artist, form)

    def _render(self, request, studio, artist, form):
        return render(request, self.template_name, {
            'studio': studio,
            'artist': artist,
            'form': form,
            'portfolio_items': artist.portfolio_items.all(),
        })


class StudioLocationsAPIView(View):
    """Endpoint leve para o mapa da home — apenas id, name, lat, lng, slug."""

    def get(self, request):
        locations = list(
            Studio.objects.filter(
                is_active=True,
                latitude__isnull=False,
                longitude__isnull=False,
            ).values('id', 'name', 'latitude', 'longitude', 'slug')
        )
        for item in locations:
            item['id'] = str(item['id'])
        return JsonResponse(locations, safe=False)
