# Generated by Django 3.2.4 on 2021-07-07 15:33

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryCompetition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.IntegerField(choices=[(1, 'Senior'), (2, 'Junior'), (3, 'Cadet'), (4, 'Open')])),
                ('problems_per_team', models.PositiveIntegerField(blank=True, null=True)),
                ('max_teams_per_school', models.PositiveIntegerField(blank=True, null=True)),
                ('max_teams_second_round', models.PositiveIntegerField(blank=True, null=True)),
                ('max_members_per_team', models.PositiveIntegerField(blank=True, null=True)),
                ('ranking', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(choices=[(1, 'Score'), (2, 'Problems'), (3, 'Time')]), size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('branch', models.IntegerField(choices=[(1, 'Math'), (2, 'Physics'), (3, 'Junior')])),
                ('graduation_year', models.PositiveIntegerField()),
                ('web_start', models.DateTimeField()),
                ('registration_start', models.DateTimeField()),
                ('registration_second_round_start', models.DateTimeField(blank=True, null=True)),
                ('registration_end', models.DateTimeField()),
                ('competition_start', models.DateTimeField()),
                ('competition_duration', models.DurationField()),
                ('is_cancelled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CompetitionProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CompetitionSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capacity', models.PositiveIntegerField(default=0)),
                ('accepted_languages', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('local_start', models.DateTimeField(blank=True, null=True)),
                ('results_announced', models.BooleanField(default=False)),
                ('participants_hidden', models.BooleanField(default=False)),
                ('email_alias', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocalizedProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.IntegerField()),
                ('statement_text', models.TextField()),
                ('result_text', models.TextField()),
                ('solution_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('short_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='SolutionSubmitLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wildcard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(blank=True)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.categorycompetition')),
            ],
        ),
    ]
