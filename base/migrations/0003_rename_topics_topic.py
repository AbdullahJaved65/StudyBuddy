# Generated by Django 4.1.5 on 2023-01-17 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_topics_room_host_message_room_topic'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Topics',
            new_name='Topic',
        ),
    ]
