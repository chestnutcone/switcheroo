# Generated by Django 2.2.1 on 2019-09-12 21:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_auto_20190912_1235'),
    ]

    operations = [
        migrations.RenameField(
            model_name='request',
            old_name='requester',
            new_name='applicant',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='requester_shift',
            new_name='applicant_schedule',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='receiver_shift',
            new_name='receiver_schedule',
        ),
        migrations.AddField(
            model_name='request',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]