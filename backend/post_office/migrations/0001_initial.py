# Generated by Django 5.1.3 on 2024-11-24 18:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PostOffice",
            fields=[
                (
                    "pincode",
                    models.CharField(max_length=10, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("contactNo", models.CharField(max_length=15)),
                ("address", models.TextField()),
                (
                    "division_pincode",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="post_office.postoffice",
                    ),
                ),
            ],
        ),
    ]
