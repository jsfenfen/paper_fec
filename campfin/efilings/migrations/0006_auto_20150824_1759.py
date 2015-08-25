# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0005_auto_20150824_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filing',
            name='discovery_method',
            field=models.CharField(help_text=b'How did we detect the filing? : R=RSS, F=find_filings, Q=query, A=Archived daily filings -- add your own here...', max_length=1, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='filing',
            name='is_amendment',
            field=models.NullBooleanField(),
        ),
    ]
