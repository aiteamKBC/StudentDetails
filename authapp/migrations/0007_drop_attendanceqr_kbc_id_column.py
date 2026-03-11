from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0006_restore_attendanceqr_create_alternative_email'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE "attendance_QR" DROP COLUMN IF EXISTS "kbc_id";',
            reverse_sql='ALTER TABLE "attendance_QR" ADD COLUMN IF NOT EXISTS "kbc_id" bigint NULL;',
        ),
    ]
