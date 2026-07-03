from django.urls import path

from studios.views import (
    PortfolioEditView,
    StudioDashboardView,
    StudioDetailView,
    StudioLocationsAPIView,
    StudioRegistrationView,
)

urlpatterns = [
    path(
        'api/studios/locations/',
        StudioLocationsAPIView.as_view(),
        name='studio-locations-api',
    ),
    path('studios/cadastrar/', StudioRegistrationView.as_view(), name='studio-register'),
    path('studios/<slug:slug>/', StudioDetailView.as_view(), name='studio-detail'),
    path('studios/<slug:slug>/dashboard/', StudioDashboardView.as_view(), name='studio-dashboard'),
    path(
        'studios/<slug:slug>/portfolio/<uuid:artist_id>/edit/',
        PortfolioEditView.as_view(),
        name='portfolio-edit',
    ),
]
