from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0007_drop_attendanceqr_kbc_id_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternativeemail',
            name='attendance_group',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
