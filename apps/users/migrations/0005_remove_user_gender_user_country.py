# Generated by Django 4.1.2 on 2022-11-07 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_user_gender"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="gender",
        ),
        migrations.AddField(
            model_name="user",
            name="country",
            field=models.CharField(
                choices=[
                    ("FR", "France"),
                    ("BE", "Belgique"),
                    ("DE", "Deutschland"),
                    ("EN", "England"),
                    ("ES", "España"),
                    ("IT", "Italia"),
                    ("LT", "Lietuva"),
                    ("PL", "Polska"),
                    ("UA", "Україна"),
                ],
                default="FR",
                max_length=3,
                verbose_name="country",
            ),
        ),
    ]
