# Generated by Django 2.0.2 on 2018-03-30 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('riot', '0004_auto_20180330_1625'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='summoner',
            unique_together={('riot_id', 'region')},
        ),
    ]
