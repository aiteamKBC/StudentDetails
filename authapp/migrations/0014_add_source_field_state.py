from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0013_add_second_alternative_email'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='alternativeemail',
                    name='source',
                    field=models.CharField(blank=True, db_column='source', default='', max_length=50),
                ),
            ],
        ),
    ]
