# -*- coding: utf-8 -*-
# Generated by Django 1.9.13.dev20170130170755 on 2018-12-05 12:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0069_blad_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pozycja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('element', models.CharField(max_length=30)),
                ('nazwa', models.CharField(max_length=255)),
                ('poziom', models.SmallIntegerField()),
                ('lp', models.SmallIntegerField()),
                ('klu1', models.CharField(max_length=10)),
                ('klu2', models.CharField(max_length=1)),
                ('klu3', models.CharField(max_length=10)),
                ('wyliczenie', models.CharField(max_length=10)),
                ('kwota_a', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('kwota_b', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('kwota_b1', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
            ],
        ),
        migrations.CreateModel(
            name='Raport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazwa', models.CharField(max_length=100)),
                ('element', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Sprawozdanie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jpk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Plik')),
            ],
        ),
        migrations.AddField(
            model_name='raport',
            name='sprawozdanie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sf.Sprawozdanie'),
        ),
        migrations.AddField(
            model_name='pozycja',
            name='raport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sf.Raport'),
        ),
    ]