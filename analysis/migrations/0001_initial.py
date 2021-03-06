# Generated by Django 2.0 on 2018-01-23 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('riot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calculation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('count', models.IntegerField()),
                ('finished', models.BooleanField()),
                ('summoner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='riot.Summoner')),
            ],
        ),
    ]
