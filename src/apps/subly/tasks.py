import logging

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from oauth2client.client import AccessTokenRefreshError
from googleapiclient.errors import HttpError

from auth import YTAuth
from video import UploadPlaylistsVideoExtractor
import message
import exceptions

logger = logging.getLogger(__name__)

# TODO: Add celery. Make UpdatePlaylistsTask a celery Task.


class UpdatePlaylistsTask(object):
    def run(self, *args, **kwargs):
        auth = YTAuth()
        videos = UploadPlaylistsVideoExtractor(auth)
        for user in self.users_to_update():
            try:
                user_videos = videos.get_videos(user)
                # TODO: Apply users filters to videos.
            except AccessTokenRefreshError:
                message.add_message(user,
                                    _("YouTube credentials have expired or been revoked. Please re-authorize"))
            except HttpError as e:
                logger.exception(e)
                # TODO: Should probably check error code here and mark to retry on certain statuses (timeouts)
                raise e
            except exceptions.InvalidCredentials:
                message.add_message(user, _("Existing YouTube credentials are invalid. Please re-authorize."))

    def users_to_update(self):
        return get_user_model().objects.filter(is_active=True).exclude(ytcredentials=None)
