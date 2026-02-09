from django.db import migrations


class Migration(migrations.Migration):
    # This migration was made a no-op because the Transaction model
    # is already created in 0001_initial. Keeping an empty migration
    # preserves a linear migration history for tests and CI.
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = []