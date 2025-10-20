# Generated manually for TeamMember full_name field change

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0005_remove_aboutuspage_company_tagline_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teammember",
            name="full_name",
            field=models.JSONField(default=dict, help_text="Full name"),
        ),
    ]
