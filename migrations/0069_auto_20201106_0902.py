# Generated by Django 2.1.4 on 2020-11-06 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dc_management', '0068_auto_20201106_0845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sftp',
            name='whitelisted',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
