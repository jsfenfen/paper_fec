# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0013_auto_20150826_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='filing',
            name='outstanding_loans',
            field=models.DecimalField(default=0, help_text=b'The total amount of outstanding loans at the end of the reporting period', null=True, max_digits=14, decimal_places=2),
        ),
        migrations.AddField(
            model_name='filing',
            name='tot_contribs',
            field=models.DecimalField(default=0, help_text=b'Total contributions, if reported', null=True, max_digits=14, decimal_places=2),
        ),
        migrations.AddField(
            model_name='filing',
            name='tot_ite_contribs',
            field=models.DecimalField(default=0, help_text=b'Total itemized contributions, if reported', null=True, max_digits=14, decimal_places=2),
        ),
        migrations.AddField(
            model_name='filing',
            name='tot_non_ite_contribs',
            field=models.DecimalField(default=0, help_text=b'Total unitemized contributions, if reported', null=True, max_digits=14, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='filing',
            name='tot_coordinated',
            field=models.DecimalField(default=0, help_text=b'Total amount of coordinated expenditures made (really only applies to party PACs.)', null=True, max_digits=14, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='filing',
            name='tot_ies',
            field=models.DecimalField(default=0, help_text=b'The total amount of independent expenditures made', null=True, max_digits=14, decimal_places=2),
        ),
    ]
