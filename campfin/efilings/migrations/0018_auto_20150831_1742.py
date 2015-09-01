# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('efilings', '0017_committee_tot_coo_exp_par'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candidate',
            old_name='total_unitemized',
            new_name='total_unitemized_indiv',
        ),
        migrations.AddField(
            model_name='committee',
            name='filing_aggregation_issue',
            field=models.CharField(default=b'0', help_text=b'D for duplicate, S for gap at start of cycle; G for gap not beginning at start of cycle; if there are multiple issues, just add the letters.', max_length=15),
        ),
        migrations.AddField(
            model_name='committee',
            name='filing_issue_message',
            field=models.TextField(default=True, help_text=b'Put the error message here', null=True),
        ),
    ]
