from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

def index(request):
    return render(request, 'global/base.html', {
        'site_title': 'Home',
        'current_menu': 'home'
    })