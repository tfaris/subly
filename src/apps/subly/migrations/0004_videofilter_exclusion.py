# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subly', '0003_auto_20150630_2330'),
    ]

    operations = [
        migrations.AddField(
            model_name='videofilter',
            name='exclusion',
            field=models.BooleanField(default=False, help_text=b'If true, videos that match this filter will be excluded from the associated playlist and not added as an unrecognized video.'),
        ),
    ]
