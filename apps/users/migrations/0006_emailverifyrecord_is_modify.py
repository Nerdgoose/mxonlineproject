# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-21 18:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20170120_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailverifyrecord',
            name='is_modify',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u6709\u6548'),
        ),
    ]
