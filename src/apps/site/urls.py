from django.conf.urls import include, url
from django.contrib import admin

from apps.site import views

urlpatterns = [
    url(r'^/?$', views.IndexView.as_view(), name='home'),

    url(r'^admin/', include(admin.site.urls)),
]
