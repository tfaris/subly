import logging

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from oauth2client.client import AccessTokenRefreshError
from googleapiclient.errors import HttpError

from auth import YTAuth
from video import UploadPlaylistsVideoExtractor
from models import VideoFilter
import message
import exceptions

logger = logging.getLogger(__name__)

# TODO: Add celery. Make UpdatePlaylistsTask a celery Task.


class UpdatePlaylistsTask(object):
    def run(self, *args, **kwargs):
        auth = YTAuth()
        videos = UploadPlaylistsVideoExtractor(auth)
        for user in self.users_to_update():
            filters = VideoFilter.objects.filter(user=user)
            if filters:
                try:
                    user_videos = videos.get_videos(user)
                    # TODO: Add videos to playlists based on filter matches.
                    for video in user_videos:
                        matches = 0
                        for f in filters:
                            match = f.matches_video(video)
                            if match:
                                matches += 1
                                logger.info("\"%s\" matches filter %s" % (video.title, f))
                        if matches == 0:
                            logger.info("\"%s\" matched no filters." % video.title)
                except AccessTokenRefreshError:
                    message.add_message(user,
                                        _("YouTube credentials have expired or been revoked. Please re-authorize"))
                except HttpError as e:
                    logger.exception(e)
                    # TODO: Should probably check error code here and mark to retry on certain statuses (timeouts)
                    raise e
                except exceptions.InvalidCredentials:
                    message.add_message(user, _("Existing YouTube credentials are invalid. Please re-authorize."))
            else:
                logger.info("Skipping user %s due to no defined video filters." % user.email)

    def users_to_update(self):
        return get_user_model().objects.filter(is_active=True).exclude(ytcredentials=None)
