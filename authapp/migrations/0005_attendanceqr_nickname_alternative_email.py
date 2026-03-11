from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0004_remove_attendanceqr_kbc_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendanceqr',
            name='alternative_email',
            field=models.EmailField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='attendanceqr',
            name='nickname',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
