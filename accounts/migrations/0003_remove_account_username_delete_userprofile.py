# Generated by Django 4.1.7 on 2023-04-28 09:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='username',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
