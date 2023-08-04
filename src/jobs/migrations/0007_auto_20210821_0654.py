# Generated by Django 3.2.6 on 2021-08-21 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_auto_20210821_0602'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='joboffer',
            options={'ordering': ['-is_enabled']},
        ),
        migrations.AddField(
            model_name='joboffer',
            name='is_enabled',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]