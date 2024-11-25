# Generated by Django 5.1.3 on 2024-11-25 19:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("post_office", "0001_initial"),
        ("waste_management", "0002_selledpaperwaste_date_alter_paperwaste_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="pincode",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="post_office.postoffice",
            ),
        ),
        migrations.AlterField(
            model_name="eventreport",
            name="pincode",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="post_office.postoffice",
            ),
        ),
    ]
