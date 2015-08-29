# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0014_auto_20150828_1353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filing',
            name='tot_ite_contribs',
        ),
        migrations.RemoveField(
            model_name='filing',
            name='tot_non_ite_contribs',
        ),
        migrations.AddField(
            model_name='filing',
            name='tot_ite_contribs_indivs',
            field=models.DecimalField(default=0, help_text=b'Total itemized contributions from individuals if reported (individuals includes corporations, unions)', null=True, max_digits=14, decimal_places=2),
        ),
        migrations.AddField(
            model_name='filing',
            name='tot_non_ite_contribs_indivs',
            field=models.DecimalField(default=0, help_text=b'Total unitemized contributions from individuals, if reported (individuals includes corporations, unions)', null=True, max_digits=14, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='filing',
            name='outstanding_loans',
            field=models.DecimalField(default=0, help_text=b'Debts and Obligations Owed BY the Committee', null=True, max_digits=14, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='filing',
            name='tot_contribs',
            field=models.DecimalField(default=0, help_text=b'Total contributions, if reported (includes individuals, pacs, etc.)', null=True, max_digits=14, decimal_places=2),
        ),
    ]
