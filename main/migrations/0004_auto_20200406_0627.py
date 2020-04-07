# Generated by Django 3.0.5 on 2020-04-06 06:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20200406_0626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tutorial',
            name='tutorial_published',
            field=models.DateField(default=datetime.datetime(2020, 4, 6, 6, 27, 31, 86033), verbose_name='date published'),
        ),
    ]
