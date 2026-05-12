from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0025_alter_college_about_alter_college_mission_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='college',
            name='hero_description',
            field=models.TextField(blank=True, help_text='Text for the hero section (ABOUT COLLEGE)', null=True),
        ),
    ]
