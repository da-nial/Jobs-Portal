# Generated by Django 3.2.5 on 2021-08-08 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('address', models.TextField(blank=True)),
                ('logo', models.ImageField(blank=True, upload_to='images')),
                ('description', models.TextField(blank=True)),
                ('link', models.URLField()),
                ('telephone_number', models.CharField(max_length=12)),
            ],
        ),
    ]
