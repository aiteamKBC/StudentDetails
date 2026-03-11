from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0005_attendanceqr_nickname_alternative_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendanceqr',
            name='alternative_email',
        ),
        migrations.RemoveField(
            model_name='attendanceqr',
            name='nickname',
        ),
        migrations.CreateModel(
            name='AlternativeEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.BigIntegerField(unique=True)),
                ('aptem_name', models.CharField(blank=True, default='', max_length=255)),
                ('group', models.CharField(blank=True, default='', max_length=255)),
                ('aptem_email', models.EmailField(max_length=255)),
                ('nickname', models.CharField(max_length=255)),
                ('alternative_email', models.EmailField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'alternative_email',
            },
        ),
    ]
