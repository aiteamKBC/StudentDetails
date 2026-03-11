from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0009_alternativeemail_student_id_primary_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternativeemail',
            name='attendance_reason',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
