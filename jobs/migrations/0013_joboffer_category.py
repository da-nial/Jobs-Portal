# Generated by Django 3.2.6 on 2021-09-04 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0012_resume'),
    ]

    operations = [
        migrations.AddField(
            model_name='joboffer',
            name='category',
            field=models.CharField(blank=True, choices=[('DA', 'Data'), ('DU', 'Design and UX'), ('E', 'Engineering'), ('FA', 'Finance and Accounting'), ('HR', 'Human Resources'), ('MC', 'Marketing and Communications'), ('O', 'Operation'), ('P', 'Product'), ('S', 'Sales'), ('OT', 'Other')], max_length=2, null=True),
        ),
    ]
