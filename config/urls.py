from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from expenses.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('users/', include('users.urls')),
    path('groups/', include('groups.urls')),
    path('expenses/', include('expenses.urls')),
    path('ai/', include('ai_mintsense.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
