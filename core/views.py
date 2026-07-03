from django.core.files.storage import default_storage
from django.db.models import Count, OuterRef, Subquery
from django.views.generic import TemplateView

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
            if studio.cover_image:
                studio.cover_url = default_storage.url(studio.cover_image)
            else:
                studio.cover_url = None

        context['featured_studios'] = studios
        return context
