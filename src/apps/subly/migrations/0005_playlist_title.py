# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subly', '0004_videofilter_exclusion'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='title',
            field=models.CharField(default=b'', max_length=100, blank=True),
        ),
    ]
