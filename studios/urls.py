from django.urls import path

from studios.views import (
    BudgetCreateView,
    HomeView,
    PortfolioEditView,
    StudioDashboardView,
    StudioDetailView,
    StudioMapAPIView,
    StudioRegistrationView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/studios/', StudioMapAPIView.as_view(), name='api-studios'),
    path('studios/cadastrar/', StudioRegistrationView.as_view(), name='studio-register'),
    path('studios/<slug:slug>/', StudioDetailView.as_view(), name='studio-detail'),
    path('studios/<slug:slug>/dashboard/', StudioDashboardView.as_view(), name='studio-dashboard'),
    path(
        'studios/<slug:slug>/portfolio/<uuid:artist_id>/edit/',
        PortfolioEditView.as_view(),
        name='portfolio-edit',
    ),
    path('studios/<slug:slug>/budget/', BudgetCreateView.as_view(), name='budget-create'),
]
