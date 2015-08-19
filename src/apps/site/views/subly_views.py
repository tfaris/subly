from django.views.generic import RedirectView, TemplateView, FormView, View
from django.http import response, JsonResponse
from django.core import urlresolvers

from mixins import TabViewMixin, LoginRequiredMixin

from apps.subly.models import Playlist, VideoFilter
from apps.subly.forms import EditVideoFilterForm


class PlaylistsView(LoginRequiredMixin, TemplateView, TabViewMixin):
    template_name = 'site/subly_playlists.html'
    tab_id = 'playlists'

    def get_context_data(self, **kwargs):
        data = super(PlaylistsView, self).get_context_data(**kwargs)
        data['playlists'] = Playlist.objects.filter(user=self.request.user).order_by('-last_update')
        return data


class PlaylistsDetailView(LoginRequiredMixin, TemplateView, TabViewMixin):
    template_name = 'site/subly_playlist_detail.html'
    tab_id = 'playlists'

    def get_context_data(self, **kwargs):
        data = super(PlaylistsDetailView, self).get_context_data(**kwargs)
        if not self.args:
            raise response.HttpResponseBadRequest
        try:
            playlist_id = self.args[0]
            data['playlist'] = playlist = Playlist.objects.get(pk=playlist_id)
            data['filters'] = filters = playlist.videofilter_set.all().order_by('-pk')
            data['filter_fields'] = VideoFilter.FIELD_CHOICES
            for flt in filters:
                flt.edit_form = EditVideoFilterForm(instance=flt)
            return data
        except Playlist.DoesNotExist:
            raise response.Http404


class VideoFilterViewMixin(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        error = None
        resp = {}
        response_code = response.HttpResponse.status_code
        src = request.POST
        filter_id = src.get('id')
        if not filter_id:
            response_code = response.HttpResponseBadRequest.status_code
            error = "id not specified."
        else:
            try:
                vf = VideoFilter.objects.get(pk=filter_id)
                if request.user != vf.playlist.user:
                    response_code = response.HttpResponseForbidden.status_code
                    error = "permission failure"
                else:
                    self.change(vf, src)
            except KeyError as ke:
                response_code = response.HttpResponseBadRequest.status_code
                error = unicode(ke)
            except VideoFilter.DoesNotExist:
                response_code = response.HttpResponseNotFound.status_code
                error = "invalid id"
        if error:
            resp['error'] = error
        return JsonResponse(resp, status=response_code)

    def change(self, vf, src):
        pass

    def parse_bool(self, bool_str):
        return bool_str.lower() == 'true'


class VideoFilterUpdate(VideoFilterViewMixin):
    """
    Updates the VideoFilter specified to the view.
    """
    def change(self, vf, src):
        vf.string = src['string']
        vf.is_regex = self.parse_bool(src['is_regex'])
        vf.ignore_case = self.parse_bool(src['ignore_case'])
        vf.exclusion = self.parse_bool(src['exclusion'])
        vf.exact = self.parse_bool(src['exact'])
        vf.channel_title = src['channel_title']
        vf.field = src['field']
        vf.save()


class VideoFilterDelete(VideoFilterViewMixin):
    """
    Deletes the VideoFilter specified to the view.
    """
    def change(self, vf, src):
        vf.delete()


class VideoFilterCreateView(LoginRequiredMixin, TemplateView):
    """
    Creates a VideoFilter for the specified playlist and returns
    HTML for editing it.
    """
    template_name = 'site/subly_filter_row.html'
    playlist = None

    def get_context_data(self, **kwargs):
        data = super(VideoFilterCreateView, self).get_context_data(**kwargs)
        opts = dict(
            playlist=self.get_playlist(),
            string="",
            field=VideoFilter.VIDEO_TITLE
        )
        vf = VideoFilter(**opts)
        vf.save()
        data['filter'] = vf
        data['filter_fields'] = VideoFilter.FIELD_CHOICES
        return data

    def get_playlist(self):
        if not self.playlist:
            playlist_id = self.request.GET.get('playlistId')
            self.playlist = Playlist.objects.get(pk=playlist_id)
        return self.playlist

    def get(self, request, *args, **kwargs):
        error = None
        response_code = response.HttpResponse.status_code
        try:
            playlist = self.get_playlist()
            if not playlist.user == request.user:
                response_code = response.HttpResponseForbidden.status_code
                error = 'permission failure'
            else:
                r = super(VideoFilterCreateView, self).get(request, *args, **kwargs)
                r.render()
                return JsonResponse(dict(
                    content=r.content
                ))
        except Playlist.DoesNotExist:
            response_code = response.HttpResponseNotFound.status_code
            error = "Invalid playlist id."
        return JsonResponse(dict(
            error=error
        ), status_code=response_code)
