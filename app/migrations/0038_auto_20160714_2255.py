# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-07-14 22:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_auto_20160713_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plik',
            name='paczka',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pliki', to='app.Paczka'),
        ),
        migrations.AlterField(
            model_name='status',
            name='storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Storage'),
        ),
    ]
