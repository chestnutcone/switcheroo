# Generated by Django 2.2.1 on 2019-10-18 19:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='employee_detail',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.EmployeeID'),
        ),
    ]