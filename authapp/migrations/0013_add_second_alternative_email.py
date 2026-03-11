from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0012_rename_alternative_email_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternativeemail',
            name='alternative_email_2',
            field=models.EmailField(blank=True, db_column='alternative_email_2', default='', max_length=255),
        ),
    ]
