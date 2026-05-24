from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='is_premium',
            field=models.BooleanField(default=False, help_text='Premium tests require an active subscription'),
        ),
    ]
