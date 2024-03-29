# Generated by Django 2.1.4 on 2020-11-06 13:45

import cidrfield.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dc_management', '0067_auto_20201105_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dcuagenerator',
            name='enddate',
            field=models.CharField(default='11/06/2021', max_length=32, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='startdate',
            field=models.CharField(default='11/06/2020', max_length=32, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='sftp',
            name='login_details',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='External login details'),
        ),
        migrations.AlterField(
            model_name='sftp',
            name='whitelisted',
            field=cidrfield.models.IPNetworkField(blank=True, null=True),
        ),
    ]
