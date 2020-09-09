# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-02-22 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cognation', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='locus',
            index=models.Index(fields=['locus', 'sat'], name='cognation_l_locus_e2fc2e_idx'),
        ),
    ]