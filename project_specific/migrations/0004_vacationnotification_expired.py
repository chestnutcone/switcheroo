# Generated by Django 2.2.1 on 2019-10-08 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_specific', '0003_vacationnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacationnotification',
            name='expired',
            field=models.BooleanField(default=False),
        ),
    ]
