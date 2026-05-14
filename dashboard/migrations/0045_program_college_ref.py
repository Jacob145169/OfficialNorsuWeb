from django.db import migrations, models
import django.db.models.deletion


def link_programs_to_colleges(apps, schema_editor):
    College = apps.get_model('dashboard', 'College')
    Program = apps.get_model('dashboard', 'Program')

    colleges_by_abbr = {
        (college.abbreviation or '').strip().lower(): college
        for college in College.objects.all()
    }
    colleges_by_name = {
        (college.name or '').strip().lower(): college
        for college in College.objects.all()
    }

    for program in Program.objects.all():
        college_key = (program.college or '').strip().lower()
        college = colleges_by_abbr.get(college_key) or colleges_by_name.get(college_key)
        if college:
            program.college_ref_id = college.id
            program.college = (college.abbreviation or '').strip().lower()
            program.save(update_fields=['college_ref', 'college'])

    for college in College.objects.all():
        College.objects.filter(pk=college.pk).update(
            programs_offered=Program.objects.filter(college_ref_id=college.pk).count()
        )


def unlink_programs_from_colleges(apps, schema_editor):
    Program = apps.get_model('dashboard', 'Program')

    for program in Program.objects.exclude(college_ref__isnull=True).select_related('college_ref'):
        program.college = (program.college_ref.abbreviation or '').strip().lower()
        program.save(update_fields=['college'])


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0044_norsuhistory_presidentprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='college_ref',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='programs',
                to='dashboard.college',
            ),
        ),
        migrations.RunPython(link_programs_to_colleges, unlink_programs_from_colleges),
    ]
