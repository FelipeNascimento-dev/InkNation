from django.urls import path
from .views import UserLoginView, LogoutConfirmView, UserLogoutView

app_name = 'inknation'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutConfirmView.as_view(), name='logout_confirm'),
    path('logout/confirm/', UserLogoutView.as_view(), name='logout'),
]