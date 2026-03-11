from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0010_alternativeemail_attendance_reason'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='alternativeemail',
                    name='student_id',
                    field=models.BigIntegerField(db_column='ID', primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name='alternativeemail',
                    name='aptem_name',
                    field=models.CharField(blank=True, db_column='FullName', default='', max_length=255),
                ),
                migrations.AlterField(
                    model_name='alternativeemail',
                    name='attendance_group',
                    field=models.CharField(blank=True, db_column='other_group', default='', max_length=255),
                ),
                migrations.AlterField(
                    model_name='alternativeemail',
                    name='attendance_reason',
                    field=models.TextField(blank=True, db_column='other_group_reason', default=''),
                ),
                migrations.AlterField(
                    model_name='alternativeemail',
                    name='aptem_email',
                    field=models.EmailField(db_column='Email', max_length=255),
                ),
            ],
        ),
    ]
