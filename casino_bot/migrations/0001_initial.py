# Generated by Django 4.1.7 on 2023-03-08 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100, null=True)),
                ('tg_uid', models.IntegerField()),
                ('balance', models.IntegerField(default=0)),
                ('stage', models.CharField(default='menu', max_length=50)),
                ('games_count', models.IntegerField(default=0)),
            ],
        ),
    ]
