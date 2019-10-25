# Generated by Django 2.2.1 on 2019-10-24 19:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule', '0001_initial'),
        ('people', '0002_auto_20191024_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacation',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.Group'),
        ),
        migrations.AddField(
            model_name='swapresult',
            name='applicant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='people.Employee'),
        ),
        migrations.AddField(
            model_name='shift',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.Group'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedule_schedule_1', to='schedule.Shift'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedule_schedule_2', to='schedule.Shift'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedule_schedule_3', to='schedule.Shift'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.Group'),
        ),
        migrations.AddField(
            model_name='request',
            name='applicant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requester', to='people.Employee'),
        ),
        migrations.AddField(
            model_name='request',
            name='applicant_schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requester_shift', to='schedule.Assign'),
        ),
        migrations.AddField(
            model_name='request',
            name='manager',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='receiver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='people.Employee'),
        ),
        migrations.AddField(
            model_name='request',
            name='receiver_schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receiver_shift', to='schedule.Assign'),
        ),
        migrations.AddField(
            model_name='assign',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='people.Employee'),
        ),
        migrations.AddField(
            model_name='assign',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.Group'),
        ),
    ]