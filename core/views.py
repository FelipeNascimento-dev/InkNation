from django.db.models import Count, OuterRef, Subquery
from django.views.generic import TemplateView

from core.utils.studio_media import resolve_studio_cover_url
from studios.models import PortfolioItem, Studio


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cover_subquery = PortfolioItem.objects.filter(
            artist__studio=OuterRef('pk'),
        ).order_by('-created_at').values('image')[:1]

        studios = (
            Studio.objects.filter(is_active=True)
            .annotate(
                artist_count=Count('artists', distinct=True),
                cover_image=Subquery(cover_subquery),
            )
            .order_by('name')[:12]
        )

        for studio in studios:
            studio.cover_url = resolve_studio_cover_url(
                studio.cover_image,
                studio.state,
            )

        context['featured_studios'] = studios
        return context
