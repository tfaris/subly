# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subly', '0005_playlist_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='videofilter',
            name='channel_title',
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
    ]
