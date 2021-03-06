from django.conf.urls import include, url
from django.contrib import admin

from apps.site import views

urlpatterns = [
    url(r'^/?$', views.IndexView.as_view(), name='home'),
    url(r'^login/?$', views.LoginView.as_view(), name='login'),
    url(r'^logout/?$', views.LogoutView.as_view(), name='logout'),
    url(r'^profile/?$', views.ProfileView.as_view(), name='profile'),

    url(r'^playlists/$', views.PlaylistsView.as_view(), name='playlists'),
    url(r'^playlists/(\d+)$', views.PlaylistsDetailView.as_view(), name='playlist_detail'),
    url(r'^playlists/(\d+)/delete/$', views.PlaylistsDeleteView.as_view(), name='playlist_delete'),
    url(r'^playlists/$', views.PlaylistsView.as_view(), name='playlist_new'),

    url(r'^playlists/filter/new/$', views.VideoFilterCreateView.as_view(), name='filter_new'),
    url(r'^playlists/filter/update/$', views.VideoFilterUpdate.as_view(), name='filter_update'),
    url(r'^playlists/filter/delete/$', views.VideoFilterDelete.as_view(), name='filter_delete'),
    
    url(r'^playlists/playlist_exclusion/new/$', views.PlaylistExclusionCreateView.as_view(), name='playlist_exclusion_new'),
    url(r'^playlists/playlist_exclusion/delete/$', views.PlaylistExclusionDeleteView.as_view(), name='playlist_exclusion_delete'),

    url(r'^messages/', include('messages_extends.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
