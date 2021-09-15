# Generated by Django 2.1.4 on 2021-07-08 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacatalog', '0023_auto_20210201_2349'),
        ('dc_management', '0070_auto_20210518_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='governance',
            field=models.ManyToManyField(blank=True, to='datacatalog.DataUseAgreement'),
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='enddate',
            field=models.CharField(default='07/07/2022', max_length=32, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='startdate',
            field=models.CharField(default='07/07/2021', max_length=32, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='location',
            field=models.CharField(choices=[('IS', 'Isilon'), ('AW', 'Amazon Web Services'), ('GL', 'AWS Glacier'), ('S3', 'AWS S3 Storage'), ('AZ', 'Microsoft Azure'), ('SA', 'Secure Remote Archive')], default='IS', max_length=2, verbose_name='Storage location'),
        ),
    ]