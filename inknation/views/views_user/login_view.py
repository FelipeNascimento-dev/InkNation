from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class UserLoginView(LoginView):
    template_name = "inknation/templates_user/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("website:index")
    

class LogoutConfirmView(TemplateView):
    template_name = "inknation/templates_user/logout.html"


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("website:index")