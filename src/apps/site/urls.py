from django.conf.urls import include, url
from django.contrib import admin

from apps.site import views

urlpatterns = [
    url(r'^/?$', views.IndexView.as_view(), name='home'),
    url(r'^login/?$', views.LoginView.as_view(), name='login'),
    url(r'^logout/?$', views.LogoutView.as_view(), name='logout'),

    url(r'^admin/', include(admin.site.urls)),
]
