import re

from django.db import models
from django.conf import settings

import fields


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

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    string = models.CharField(blank=True, max_length=150)
    ignore_case = models.BooleanField(default=True)
    field = models.PositiveSmallIntegerField(choices=FIELD_CHOICES)
    is_regex = models.BooleanField(default=False)
    exact = models.BooleanField(default=False,
                                help_text="Indicates whether the match has to be exact or just contained. Not "
                                          "applicable if the filter is a regular expression.")

    def matches_video(self, video):
        """
        Returns True if this filter matches the specified Video instance.
        :type video: video.Video
        :return:
        """
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
        return 'string="%s", field=%s, exact=%s, ignore_case=%s' % (self.string,
                                                                    match_field_type, self.exact, self.ignore_case)
