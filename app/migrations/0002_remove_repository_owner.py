# Generated by Django 2.2.2 on 2019-08-11 20:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repository',
            name='owner',
        ),
    ]
