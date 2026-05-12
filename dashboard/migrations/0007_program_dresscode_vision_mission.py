from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_program_objectives'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='dresscode_schedule',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='dresscode_images',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='vision',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='mission',
            field=models.TextField(blank=True, null=True),
        ),
    ]
