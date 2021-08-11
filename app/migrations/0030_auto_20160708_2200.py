# -*- coding: utf-8 -*-
# Generated by Django 1.9.8.dev20160628165209 on 2016-07-08 22:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_plik_magazyn'),
    ]

    operations = [
        migrations.CreateModel(
            name='MagKart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dzial', models.CharField(max_length=3)),
                ('data_kart', models.DateField()),
                ('indeks', models.CharField(max_length=20)),
                ('partia', models.CharField(max_length=10)),
                ('data_prod', models.DateField()),
                ('data_wazn', models.DateField()),
                ('saldo_il', models.DecimalField(decimal_places=3, max_digits=12)),
                ('saldo_dysp', models.DecimalField(decimal_places=3, max_digits=12)),
                ('cena_ewid', models.DecimalField(decimal_places=2, max_digits=12)),
                ('lokaliza', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='MagTowar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dzial', models.CharField(max_length=3)),
                ('indeks', models.CharField(max_length=20)),
                ('nazwa', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='magkart',
            name='id_towar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.MagTowar'),
        ),
    ]
