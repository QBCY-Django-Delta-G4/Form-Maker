from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('dynamic_forms.urls')),
    path('api/', include('dynamic_forms.api.urls')),

]
