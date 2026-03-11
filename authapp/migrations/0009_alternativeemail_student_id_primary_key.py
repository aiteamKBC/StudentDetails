from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0008_alternativeemail_attendance_group'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE "alternative_email" DROP CONSTRAINT IF EXISTS "alternative_email_pkey";
                    ALTER TABLE "alternative_email" DROP CONSTRAINT IF EXISTS "alternative_email_student_id_key";
                    ALTER TABLE "alternative_email" RENAME COLUMN "student_id" TO "Student_ID";
                    ALTER TABLE "alternative_email" DROP COLUMN IF EXISTS "id";
                    ALTER TABLE "alternative_email" ADD PRIMARY KEY ("Student_ID");
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='alternativeemail',
                    name='id',
                ),
                migrations.AlterField(
                    model_name='alternativeemail',
                    name='student_id',
                    field=models.BigIntegerField(db_column='Student_ID', primary_key=True, serialize=False),
                ),
            ],
        ),
    ]
