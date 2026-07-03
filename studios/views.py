from django.contrib import messages
from django.db import transaction
from django.db.models import Count, OuterRef, Subquery
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, TemplateView, View

from budgets.forms import BudgetRequestForm
from budgets.models import BUDGET_STATUS_IN_ANALYSIS, BUDGET_STATUS_SENT, BudgetRequest
from core.constants import STUDIO_OWNER, STUDIO_STAFF
from core.mixins import RoleRequiredMixin, StudioOwnerRequiredMixin, StudioStaffOrOwnerMixin
from core.utils.studio_access import (
    user_can_manage_studio,
    user_can_request_budget,
    user_can_view_studio,
    user_is_studio_owner,
    user_is_studio_staff,
)
from core.utils.studio_media import resolve_studio_cover_absolute, resolve_studio_cover_for_instance
from studios.forms import PortfolioItemForm, StudioRegistrationForm, TattooArtistForm
from studios.models import PortfolioItem, Studio, StudioApprovalRequest, TattooArtist


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
        if user_can_view_studio(self.request.user, studio):
            return studio
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        studio = self.object
        context['can_manage'] = user_can_manage_studio(user, studio)
        can_request_budget = user_can_request_budget(user, studio)
        context['can_request_budget'] = can_request_budget
        context['studio_cover_url'] = resolve_studio_cover_for_instance(studio)
        context['artist_count'] = studio.artists.count()
        if can_request_budget:
            context['budget_form'] = BudgetRequestForm(studio=studio)
        return context


class StudioDashboardView(StudioStaffOrOwnerMixin, TemplateView):
    template_name = 'studios/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        studio = self.get_studio()
        user = self.request.user
        is_owner = user_is_studio_owner(user, studio)
        is_staff = user_is_studio_staff(user, studio)
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
            'recent_budgets': budget_qs.select_related(
                'client', 'artist',
            ).order_by('-created_at')[:20],
            'artist_form': TattooArtistForm(studio=studio) if is_owner else None,
        })
        return context


class TattooArtistCreateView(StudioOwnerRequiredMixin, View):
    def post(self, request, slug):
        studio = self.get_studio()
        form = TattooArtistForm(request.POST, studio=studio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artista cadastrado com sucesso.')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
        return redirect('studio-dashboard', slug=slug)


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
    """Endpoint leve para o mapa da home."""

    def get(self, request):
        cover_subquery = PortfolioItem.objects.filter(
            artist__studio=OuterRef('pk'),
        ).order_by('-created_at').values('image')[:1]

        studios = (
            Studio.objects.filter(
                is_active=True,
                latitude__isnull=False,
                longitude__isnull=False,
            )
            .annotate(
                artist_count=Count('artists', distinct=True),
                cover_image=Subquery(cover_subquery),
            )
            .values(
                'id', 'name', 'latitude', 'longitude', 'slug',
                'city', 'state', 'artist_count', 'cover_image',
            )
        )

        locations = []
        for item in studios:
            entry = {
                'id': str(item['id']),
                'name': item['name'],
                'latitude': item['latitude'],
                'longitude': item['longitude'],
                'slug': item['slug'],
                'city': item['city'],
                'state': item['state'],
                'artist_count': item['artist_count'],
            }
            entry['cover_url'] = resolve_studio_cover_absolute(
                request,
                item['cover_image'],
                item['state'],
            )
            locations.append(entry)

        return JsonResponse(locations, safe=False)
