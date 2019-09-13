# Generated by Django 2.2.1 on 2019-09-13 04:04

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(help_text='start day for shift')),
                ('shift_start', models.DateTimeField()),
                ('shift_end', models.DateTimeField()),
                ('switch', models.BooleanField(default=False)),
                ('individual', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='people.Individual')),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shift_start', models.TimeField(help_text='enter format hh:mm:ss')),
                ('shift_duration', models.DurationField(help_text='enter format hh:mm:ss')),
                ('shift_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('schedule_name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('cycle', models.PositiveSmallIntegerField(help_text='how many days is the shift pattern cycle', verbose_name=django.core.validators.MaxValueValidator(10))),
                ('day_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedule_schedule_1', to='schedule.Shift')),
                ('day_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedule_schedule_2', to='schedule.Shift')),
                ('day_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='schedule_schedule_3', to='schedule.Shift')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('accept', models.BooleanField(default=False)),
                ('done', models.BooleanField(default=False)),
                ('applicant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requester', to='people.Individual')),
                ('applicant_schedule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requester_shift', to='schedule.Assign')),
                ('receiver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='people.Individual')),
                ('receiver_schedule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receiver_shift', to='schedule.Assign')),
            ],
        ),
    ]
