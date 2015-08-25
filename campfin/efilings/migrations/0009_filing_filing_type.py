# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0008_auto_20150825_0121'),
    ]

    operations = [
        migrations.AddField(
            model_name='filing',
            name='filing_type',
            field=models.CharField(help_text=b'Filing type: E = electronic, P = paper, S = experimental senate filing', max_length=1, null=True),
        ),
    ]
