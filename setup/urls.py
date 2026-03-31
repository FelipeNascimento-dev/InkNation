from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('inknation/', include('inknation.urls')),
    path('inknation/', include('website.urls')),
    path('admin/', admin.site.urls),
]
