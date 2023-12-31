# Generated by Django 3.2.6 on 2021-08-25 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0010_alter_joboffer_managers'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingApplication',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('jobs.application',),
        ),
        migrations.AlterModelManagers(
            name='joboffer',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='application',
            name='reject_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Reject Reason'),
        ),
        migrations.AlterField(
            model_name='application',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to='resumes/', verbose_name='Resume'),
        ),
    ]
