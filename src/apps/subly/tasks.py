import logging

import dateutil.parser

import celery

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.db import transaction

from oauth2client.client import AccessTokenRefreshError
from googleapiclient.errors import HttpError

from auth import YTAuth
from video import UploadPlaylistsVideoExtractor
from models import Playlist, UnrecognizedVideo
import message
import exceptions

logger = logging.getLogger(__name__)


class UpdatePlaylistsTask(celery.Task):
    def run(self, *args, **kwargs):
        auth = YTAuth()
        videos = UploadPlaylistsVideoExtractor(auth)
        for user in self.users_to_update():
            with transaction.atomic():
                playlists = Playlist.objects.filter(user=user)
                if playlists:
                    try:
                        video_match_count = {}
                        video_outdated_count = {}
                        playlist_videos = {}
                        playlist_exclusions = {}
                        unrecognized_batch = []
                        user_videos = videos.get_videos(user)
                        for video in user_videos:
                            try:
                                published_timestamp = dateutil.parser.parse(video.publishedAt)
                                for playlist in playlists:
                                    # Only check videos for a filter match if their publish date is newer than the
                                    # last time this playlist was updated.
                                    if not playlist.last_update or published_timestamp >= playlist.last_update:
                                        for f in playlist.videofilter_set.all():
                                            match = f.matches_video(video)
                                            if match:
                                                video_match_count[video] = video_match_count.setdefault(video, 0) + 1
                                                logger.info("\"%s\" matches filter %s" % (video.title, f))
                                                vid_list = playlist_videos.setdefault(playlist, [])
                                                if f.exclusion:
                                                    playlist_exclusions.setdefault(playlist, []).append(video)
                                                    # Remove all instances of the video, in case it somehow got added
                                                    # multiple times.
                                                    while video in vid_list:
                                                        vid_list.remove(video)
                                                else:
                                                    if (video not in vid_list
                                                       and video not in playlist_exclusions.setdefault(playlist, [])):
                                                        vid_list.append(video)
                                    else:
                                        video_outdated_count[video] = video_outdated_count.setdefault(video, 0) + 1
                                # After the initial matching, check playlist-level exclusions
                                for playlist in playlists:
                                    this_list_matches = playlist_videos.get(playlist, [])
                                    for exclusion_playlist in playlist.exclude_when_matches_playlist.all():
                                        if exclusion_playlist != playlist:
                                            exclusion_list_matches = playlist_videos.get(exclusion_playlist, [])
                                            for vid in list(this_list_matches):
                                                if vid in exclusion_list_matches:
                                                    this_list_matches.remove(vid)
                                                    playlist_exclusions.setdefault(playlist, []).append(vid)
                                                    logger.info("\"%s\" matches playlist \"%s\", but also matches playlist \"%s\", so is excluded." % (video.title, playlist.title, exclusion_playlist.title))
                                            
                                # If the video had no matches in any playlists, and its not out of date with all
                                # playlists, add to the unrecognized videos batch so the user can review it later.
                                if (video_match_count.setdefault(video, 0) == 0 and
                                        video_outdated_count.setdefault(video, 0) == 0):
                                    unrecognized_batch.append(
                                        UnrecognizedVideo(user=user, title=video.title[:100],
                                                          channel_title=video.channel_title[:100])
                                    )
                                    logger.info("\"%s\" matched no filters." % video.title)
                            except (AttributeError, ValueError) as ex:
                                logger.exception(ex)
                        if unrecognized_batch:
                            UnrecognizedVideo.objects.bulk_create(unrecognized_batch)
                        # Add videos to playlists in batch.
                        for playlist, videos in playlist_videos.items():
                            playlist.add_videos(auth, videos)
                        if len(unrecognized_batch) + len(playlist_videos) == 0:
                            logger.info("Nothing to update for user \"%s\"." % (user.email,))
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
