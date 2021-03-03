# Generated by Django 3.1.7 on 2021-03-03 01:04

import address.models
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0003_auto_20200830_1851'),
        ('app', '0006_auto_20210225_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='address',
            field=address.models.AddressField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='address.address'),
        ),
    ]
