# Generated by Django 2.2.9 on 2021-02-18 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20210217_2337'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
    ]
