# Generated by Django 2.2.1 on 2019-09-12 03:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_choice', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_choice', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('person_email', models.EmailField(max_length=254)),
                ('employee_id', models.IntegerField(help_text='enter employee id', primary_key=True, serialize=False)),
                ('accept_swap', models.BooleanField(default=False)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('person_position', models.ForeignKey(help_text='select a position', null=True, on_delete=django.db.models.deletion.SET_NULL, to='people.Position')),
                ('person_unit', models.ForeignKey(help_text='select a unit', null=True, on_delete=django.db.models.deletion.SET_NULL, to='people.Unit')),
            ],
        ),
    ]
