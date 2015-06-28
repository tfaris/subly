# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subly', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string', models.CharField(max_length=150, blank=True)),
                ('ignore_case', models.BooleanField(default=True)),
                ('field', models.PositiveSmallIntegerField(choices=[(1, b'Video Title'), (2, b'Channel Title'), (3, b'Video Description'), (4, b'Tags')])),
                ('is_regex', models.BooleanField(default=False)),
                ('exact', models.BooleanField(default=False, help_text=b'Indicates whether the match has to be exact or just contained. Not applicable if the filter is a regular expression.')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
