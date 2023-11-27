# Generated by Django 4.2.7 on 2023-11-25 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0016_remove_users_is_superuser"),
    ]

    operations = [
        migrations.AddField(
            model_name="users",
            name="is_superuser",
            field=models.BooleanField(
                default=False,
                help_text="Designates that this user has all permissions without explicitly assigning them.",
                verbose_name="superuser status",
            ),
        ),
    ]
