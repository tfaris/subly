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
