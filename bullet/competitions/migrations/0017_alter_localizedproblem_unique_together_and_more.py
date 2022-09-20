# Generated by Django 4.1.1 on 2022-09-18 00:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("competitions", "0016_venue_is_online"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="localizedproblem",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="localizedproblem",
            name="problem",
        ),
        migrations.RemoveField(
            model_name="solutionsubmitlog",
            name="problem",
        ),
        migrations.RemoveField(
            model_name="solutionsubmitlog",
            name="staff",
        ),
        migrations.RemoveField(
            model_name="solutionsubmitlog",
            name="team",
        ),
        migrations.DeleteModel(
            name="CompetitionProblem",
        ),
        migrations.DeleteModel(
            name="LocalizedProblem",
        ),
        migrations.DeleteModel(
            name="Problem",
        ),
        migrations.DeleteModel(
            name="SolutionSubmitLog",
        ),
    ]