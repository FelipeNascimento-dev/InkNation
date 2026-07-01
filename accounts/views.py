import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, View

from accounts.forms import UserRegistrationForm
from accounts.models import CustomUser


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class UserRegistrationView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Conta criada com sucesso.')
        return response
