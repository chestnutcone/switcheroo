# Generated by Django 2.2.1 on 2019-09-12 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0005_auto_20190911_2224'),
        ('schedule', '0003_auto_20190911_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assign',
            name='individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='people.Individual'),
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accept', models.BooleanField(default=False)),
                ('done', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='people.Individual')),
                ('receiver_shift', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receiver_shift', to='schedule.Assign')),
                ('requester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requester', to='people.Individual')),
                ('requester_shift', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requester_shift', to='schedule.Assign')),
            ],
        ),
    ]