# Generated by Django 4.1.5 on 2023-01-13 20:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_alter_post_published_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='published_at',
        ),
        migrations.RemoveField(
            model_name='post',
            name='updated_at',
        ),
    ]
