from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from Store.views import custom_404_handler

handler404 = custom_404_handler

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("Store.urls")),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)