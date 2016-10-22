# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subly', '0006_videofilter_channel_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='exclude_when_matches_playlist',
            field=models.ManyToManyField(to='subly.Playlist'),
        ),
    ]
