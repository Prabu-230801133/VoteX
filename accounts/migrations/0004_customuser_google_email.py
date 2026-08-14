from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_signupotp'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='google_email',
            field=models.EmailField(
                blank=True,
                help_text='College Google account used for Google OAuth login',
                max_length=254,
                null=True,
                unique=True,
            ),
        ),
    ]