# Generated by Django 2.0 on 2018-11-20 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dc_management', '0047_auto_20180915_0854'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='myapp',
            field=models.NullBooleanField(verbose_name='MyApps RDP created'),
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='enddate',
            field=models.CharField(default='11/20/2019', max_length=32, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='startdate',
            field=models.CharField(default='11/20/2018', max_length=32, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='governance_doc',
            name='governance_type',
            field=models.CharField(choices=[('IR', 'WCM IRB'), ('IX', 'IRB Exemption'), ('DU', 'DUA'), ('DC', 'D-Core User Agreement'), ('ON', 'Onboarding Form')], default='DC', max_length=2),
        ),
        migrations.AlterField(
            model_name='project',
            name='isolate_data',
            field=models.NullBooleanField(verbose_name='data isolation: isolate?'),
        ),
        migrations.AlterField(
            model_name='project',
            name='open_allowed',
            field=models.NullBooleanField(verbose_name='classification: public?'),
        ),
        migrations.AlterField(
            model_name='project',
            name='open_enabled',
            field=models.NullBooleanField(verbose_name='security: open?'),
        ),
    ]