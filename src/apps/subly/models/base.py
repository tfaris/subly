import re
import json
import logging
from datetime import timedelta


from django.db import models
from django.conf import settings
from django.utils import timezone

import fields
from .. import video

logger = logging.getLogger(__name__)


class YTCredentialsManager(models.Manager):
    def most_recent(self, user):
        """
        Get the most recent credentials for the specified user.
        """
        return YTCredentials.objects.filter(user=user).order_by('-date_created').first()


class YTCredentials(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    creds = fields.CredentialsField()
    date_created = models.DateTimeField(auto_now_add=True)

    objects = YTCredentialsManager()


class ExternalResource(models.Model):
    """
    Represents a resource belonging to an external system.
    """
    resource_max_length = 40
    resource_id = models.CharField(max_length=resource_max_length)

    class Meta:
        abstract = True

    def get(self, auth, user=None):
        raise NotImplementedError


class ExternalPlaylist(ExternalResource):
    """
    Represents a playlist maintained by an external system (eg., youtube)
    """
    active = models.BooleanField(default=True)

    def get(self, auth, user=None):
        ve = video.VideoExtractor(auth)
        return ve.get_playlists(ve.get_service(user), (self.resource_id,))[0]


class Playlist(models.Model):
    """
    Represents an internally-tracked playlist.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    youtube_playlists = models.ManyToManyField(ExternalPlaylist)
    exclude_when_matches_playlist = models.ManyToManyField('Playlist')
    last_update = models.DateTimeField(null=True, blank=True)
    title = models.CharField(blank=True, max_length=100, default="")    

    def create_external_playlist(self, video_extractor, service):
        now = timezone.now()
        from django.conf import settings
        version = settings.VERSION
        timestamp = now.strftime("%Y-%d-%m")
        playlist_name = (self.title + ' ' if self.title else ' ') + '%s [subly %s]' % (
            unicode(self.youtube_playlists.count() + 1),
            timestamp
        )
        logger.info("Creating playlist \"%s\" for user." % playlist_name)
        p = video_extractor.create_playlist(service,
                                            playlist_name,
                                            description="Playlist created by subly v%s %s" % (version, timestamp),
                                            tags=['subly'])
        ext_playlist = ExternalPlaylist(resource_id=p.id, active=True)
        ext_playlist.save()
        # Deactive all other tracked playlists for this playlist
        self.youtube_playlists.update(active=False)
        self.youtube_playlists.add(ext_playlist)
        return ext_playlist

    def add_videos(self, auth, videos):
        #
        # NOTE: As of 07-16-2015, the youtube v3 API BatchHttpRequest does not
        # work with adding videos to playlists. It is a known problem, see
        # https://groups.google.com/forum/#!msg/google-api-javascript-client/9Qdf0LCYSZs/MOcYxFKtWMQJ
        #
        if videos:
            now = timezone.now()
            ve = video.VideoExtractor(auth)
            service = ve.get_service(self.user)
            ext_playlist = self.youtube_playlists.filter(active=True).last()
            ext_playlist_vid_count = 0
            if not ext_playlist:
                ext_playlist = self.create_external_playlist(ve, service)
            else:
                # Validate the external playlist
                try:
                    pl = ext_playlist.get(auth, self.user)
                    if pl.item_count is not None and pl.item_count >= ve.PLAYLIST_MAX:
                        ext_playlist = self._create_next_playlist(ext_playlist, auth, ve, service, actual_playlist=pl)
                    ext_playlist_vid_count = pl.item_count or 0
                except Exception as ex:
                    logger.exception(ex)
                    ext_playlist = self.create_external_playlist(ve, service)
            for vid in videos:
                if ext_playlist_vid_count >= ve.PLAYLIST_MAX:
                    ext_playlist = self._create_next_playlist(ext_playlist, auth, ve, service)
                    ext_playlist_vid_count = 0
                ve.get_playlist_insert_request(service, ext_playlist.resource_id, vid.id).execute()
                ext_playlist_vid_count += 1
            if self.last_update is None and self.youtube_playlists.count() == 0:
                # Give the playlist an initial window to find videos (may not apply, depending on how active the
                # user's subscriptions are)
                self.last_update = now - timedelta(days=1)
            self.last_update = now
            self.save()

    def _create_next_playlist(self, ext_playlist, auth, video_extractor, service, actual_playlist=None):
        pl = actual_playlist or ext_playlist.get(auth, self.user)
        logger.info("Playlist \"%s\" for %s has reached the video limit. Creating a new playlist..." % (
            pl.title, self.user))
        return self.create_external_playlist(video_extractor, service)

    def get_total_video_count(self):
        """
        Get the total number of videos in the external playlists tracked by this
        playlist.
        """
        from ..auth import YTAuth
        auth = YTAuth()
        total = 0
        for ext_pl in self.youtube_playlists.all():
            try:
                pl = ext_pl.get(auth, self.user)
                if pl.item_count is not None:
                    total += pl.item_count
            except Exception as ex:
                logger.exception(ex)
        return total
    
    def __unicode__(self):
        return 'title="%s", last_updated="%s"' % (self.title, self.last_update)


class UnrecognizedVideo(models.Model):
    """
    Represents a video that was unmatched by any VideoFilter.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=100)
    channel_title = models.CharField(max_length=100)

    def get(self):
        return video.Video(dict(
            snippet=dict(
                title=self.title,
                channelTitle=self.channel_title
            )
        ))


class VideoFilter(models.Model):
    VIDEO_TITLE = 1
    CHANNEL_TITLE = 2
    VIDEO_DESC = 3
    TAGS = 4
    FIELD_CHOICES = (
        (VIDEO_TITLE, 'Video Title'),
        (CHANNEL_TITLE, 'Channel Title'),
        (VIDEO_DESC, 'Video Description'),
        (TAGS, 'Tags')
    )

    playlist = models.ForeignKey(Playlist)
    string = models.CharField(blank=True, max_length=150)
    channel_title = models.CharField(blank=True, null=True, max_length=40)
    ignore_case = models.BooleanField(default=True)
    field = models.PositiveSmallIntegerField(choices=FIELD_CHOICES)
    is_regex = models.BooleanField(default=False)
    exact = models.BooleanField(default=False,
                                help_text="Indicates whether the match has to be exact or just contained. Not "
                                          "applicable if the filter is a regular expression.")
    exclusion = models.BooleanField(default=False,
                                    help_text="If true, videos that match this filter will be excluded from the"
                                              " associated playlist and not added as an unrecognized video.")

    def matches_video(self, video):
        """
        Returns True if this filter matches the specified Video instance.
        :type video: video.Video
        :return:
        """
        if self.channel_title and not self.channel_title == video.channel_title:
            return False
        if self.field == self.TAGS:
            # Tags should be a list of strings. If we find one that matches, it's a success.
            for tag in video.tags:
                if self.compare(tag):
                    return True
            return False
        else:
            return self.compare({
                self.VIDEO_TITLE: video.title,
                self.CHANNEL_TITLE: video.channel_title,
                self.VIDEO_DESC: video.description
            }[self.field])

    def compare(self, value):
        if self.is_regex:
            flags = 0
            if self.ignore_case:
                flags = re.IGNORECASE
            return bool(re.match(self.string, value, flags=flags))
        else:
            if self.exact:
                    return self.string == value
            else:
                if self.ignore_case:
                    return self.string.lower() in value.lower()
                else:
                    return self.string in value

    def __unicode__(self):
        try:
            match_field_type = filter(lambda c: c[0] == self.field, self.FIELD_CHOICES)[0][1]
        except IndexError:
            match_field_type = 'Unknown'
        return 'string="%s", field=%s, exact=%s, ignore_case=%s, exclusion=%s' % (
            self.string, match_field_type, self.exact, self.ignore_case, self.exclusion)
