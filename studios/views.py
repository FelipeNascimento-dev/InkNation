from django.contrib import messages
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, TemplateView, View

from budgets.forms import BudgetRequestForm
from core.mixins import RoleRequiredMixin, StudioOwnerOrStaffRequiredMixin
from studios.forms import PortfolioItemForm, StudioRegistrationForm
from studios.models import PortfolioItem, Studio, StudioApprovalRequest, TattooArtist


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_studios'] = (
            Studio.objects.filter(is_active=True)
            .prefetch_related('artists__portfolio_items')[:8]
        )
        return context


class StudioMapAPIView(View):
    def get(self, request):
        studios = (
            Studio.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    'artists__portfolio_items',
                    queryset=PortfolioItem.objects.order_by('-created_at'),
                )
            )
        )
        data = []
        for studio in studios:
            featured_image = None
            for artist in studio.artists.all():
                items = artist.portfolio_items.all()
                if items:
                    featured_image = items[0].image.url
                    break
            data.append({
                'name': studio.name,
                'slug': studio.slug,
                'latitude': float(studio.latitude),
                'longitude': float(studio.longitude),
                'city': studio.city,
                'featured_image': featured_image,
            })
        return JsonResponse(data, safe=False)


class StudioRegistrationView(RoleRequiredMixin, CreateView):
    model = Studio
    form_class = StudioRegistrationForm
    template_name = 'studios/register.html'
    allowed_roles = ('owner',)

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

    def get_success_url(self):
        return reverse('studio-detail', slug=self.object.slug)


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
        from django.http import Http404
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget_form'] = BudgetRequestForm(studio=self.object)
        context['can_request_budget'] = (
            self.request.user.is_authenticated
            and self.request.user.role == 'client'
        )
        return context


class StudioDashboardView(StudioOwnerOrStaffRequiredMixin, TemplateView):
    template_name = 'studios/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        studio = self.get_studio()
        context['studio'] = studio
        context['is_owner'] = self.request.user.role == 'owner'
        context['is_staff'] = self.request.user.role == 'staff'
        context['budget_count'] = studio.budget_requests.count()
        context['artist_count'] = studio.artists.filter(is_active=True).count()
        context['pending_budgets'] = studio.budget_requests.filter(status='sent').count()
        return context


class PortfolioEditView(StudioOwnerOrStaffRequiredMixin, View):
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
        from django.shortcuts import render
        return render(request, self.template_name, {
            'studio': studio,
            'artist': artist,
            'form': form,
            'portfolio_items': artist.portfolio_items.all(),
        })


class BudgetCreateView(RoleRequiredMixin, View):
    allowed_roles = ('client',)

    def post(self, request, slug):
        studio = get_object_or_404(Studio, slug=slug, is_active=True)
        form = BudgetRequestForm(request.POST, request.FILES, studio=studio)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.client = request.user
            budget.studio = studio
            budget.save()
            messages.success(request, 'Solicitação de orçamento enviada.')
        else:
            messages.error(request, 'Não foi possível enviar o orçamento. Verifique os dados.')
        return redirect('studio-detail', slug=slug)
