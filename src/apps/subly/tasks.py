import logging

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from oauth2client.client import AccessTokenRefreshError
from googleapiclient.errors import HttpError

from auth import YTAuth
import message
import exceptions

logger = logging.getLogger(__name__)

# TODO: Add celery. Make UpdatePlaylistsTask a celery Task.


class UpdatePlaylistsTask(object):
    def run(self, *args, **kwargs):

        auth = YTAuth()
        for user in self.users_to_update():
            try:
                youtube = auth.get_service(user)
                try:
                    # Gather a list of all IDs of the channels that the user is subscribed to.
                    sub_ids = []
                    request = youtube.subscriptions().list(part='snippet', mine=True, maxResults=50)
                    while request is not None:
                        subs = request.execute()
                        for item in subs.get('items', []):
                            sub_ids.append(item['snippet']['resourceId']['channelId'])
                        request = youtube.subscriptions().list_next(request, subs)
                    # TODO: Get video list using sub_ids. Not sure which API yet. Don't want to have to query for
                    # TODO: each subscription as that becomes costly and slow very quickly.
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
