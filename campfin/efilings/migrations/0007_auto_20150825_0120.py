# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0006_auto_20150824_1759'),
    ]

    operations = [
        migrations.RenameField(
            model_name='filing',
            old_name='filing_number',
            new_name='filing_id',
        ),
    ]
