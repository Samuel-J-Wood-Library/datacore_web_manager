# Generated by Django 2.1.4 on 2019-01-17 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dc_management', '0050_auto_20190103_1326'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DC_User',
            new_name='Person',
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='enddate',
            field=models.CharField(default='01/17/2020', max_length=32, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='startdate',
            field=models.CharField(default='01/17/2019', max_length=32, verbose_name='Start Date'),
        ),
    ]