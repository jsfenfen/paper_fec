# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0016_auto_20150828_2314'),
    ]

    operations = [
        migrations.AddField(
            model_name='committee',
            name='tot_coo_exp_par',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=2),
        ),
    ]
