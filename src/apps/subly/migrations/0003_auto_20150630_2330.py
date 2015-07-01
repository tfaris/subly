# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subly', '0002_videofilter'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalPlaylist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_id', models.CharField(max_length=40)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_update', models.DateTimeField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('youtube_playlists', models.ManyToManyField(to='subly.ExternalPlaylist')),
            ],
        ),
        migrations.CreateModel(
            name='UnrecognizedVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('channel_title', models.CharField(max_length=100)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='videofilter',
            name='user',
        ),
        migrations.AddField(
            model_name='videofilter',
            name='playlist',
            field=models.ForeignKey(default=0, to='subly.Playlist'),
            preserve_default=False,
        ),
    ]
