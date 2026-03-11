from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0011_align_alternativeemail_model_with_existing_table'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE IF EXISTS "alternative_email" RENAME TO "student_alternative_details";',
                    reverse_sql='ALTER TABLE IF EXISTS "student_alternative_details" RENAME TO "alternative_email";',
                ),
            ],
            state_operations=[
                migrations.AlterModelTable(
                    name='alternativeemail',
                    table='student_alternative_details',
                ),
            ],
        ),
    ]
