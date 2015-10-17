from django.conf.urls import include, url
from django.contrib import admin

from apps.site import views

urlpatterns = [
    url(r'^/?$', views.IndexView.as_view(), name='home'),
    url(r'^login/?$', views.LoginView.as_view(), name='login'),
    url(r'^logout/?$', views.LogoutView.as_view(), name='logout'),

    url(r'^playlists/$', views.PlaylistsView.as_view(), name='playlists'),
    url(r'^playlists/(\d+)$', views.PlaylistsDetailView.as_view(), name='playlist_detail'),
    url(r'^playlists/(\d+)/delete/$', views.PlaylistsDeleteView.as_view(), name='playlist_delete'),
    url(r'^playlists/$', views.PlaylistsView.as_view(), name='playlist_new'),

    url(r'^playlists/filter/new/$', views.VideoFilterCreateView.as_view(), name='filter_new'),
    url(r'^playlists/filter/update/$', views.VideoFilterUpdate.as_view(), name='filter_update'),
    url(r'^playlists/filter/delete/$', views.VideoFilterDelete.as_view(), name='filter_delete'),

    url(r'^messages/', include('messages_extends.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
