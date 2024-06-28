from django.views.generic.detail import DetailView
from problems.models import Problem, ProblemStat, ProblemStatement
from education.models import School
from users.models import Team
from django.utils.translation import get_language
import matplotlib.pyplot as plt
from io import StringIO

import seaborn as sns
import seaborn.objects as so
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter
import base64


class ProblemStatisticsView(DetailView):
    model = Problem
    template_name = "archive/problem_statistics.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["problem"] = ProblemStatement.objects.filter(
            problem=self.object, language=get_language()
        ).first()
        ctx["stats"] = ProblemStat.objects.filter(problem=self.object)

        r = (
            ProblemStat.objects.filter(problem=self.object)
            .exclude(solve_duration__isnull=True)
            .exclude(team__language="fa")
            .to_dataframe(
                [
                    "solve_duration",
                    "team__language",
                    "team__venue__category__identifier",
                ]
            )
            .astype({"solve_duration": "timedelta64[ns]"})
        )
        epoch = pd.Timestamp("1970-01-01")
        r["solve_duration"] = r["solve_duration"] + epoch
        plots = []
        for category in r["team__venue__category__identifier"].unique():
            s = StringIO()
            plt.figure()
            sns.set(font_scale=1.5)
            sns.set_style("whitegrid")
            g = sns.displot(
                r.query("team__venue__category__identifier == @category"),
                x="solve_duration",
                hue="team__language",
                kind="kde",
            )
            plt.gcf().set_size_inches(12, 6)

            g.set(
                title=f"Problem solving time Distribution for {self.object}",
                xlabel="Solving time",
                ylabel="Number of teams",
            )

            g._legend.set(title="Language")
            date_form = DateFormatter("%H:%M:%S")
            plt.gca().xaxis.set_major_formatter(date_form)
            plt.xlim(0, None)
            locs, labels = plt.xticks()
            plt.setp(labels, rotation=45, ha="right", rotation_mode="anchor")
            plt.savefig(s, format="svg")
            plt.close()
            plots.append(base64.b64encode(bytes(s.getvalue(), "utf-8")).decode("utf-8"))

        ctx["plots"] = plots
        return ctx


class SchoolStatisticsView(DetailView):
    model = School
    template_name = "archive/school_statistics.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["school"] = self.object

        s = StringIO()
        teams = Team.objects.filter(school=self.object)

        r = (
            ProblemStat.objects.filter(team__in=teams)
            .exclude(solved_time__isnull=True)
            .exclude(team__language="fa")
            .to_dataframe(
                [
                    "solved_time",
                    "team__in_school_symbol",
                    "team__venue__category__identifier",
                    "team__venue__category__competition",
                ]
            )
            .astype({"solved_time": "timedelta64[ns]"})
        )
        print(r)
        epoch = pd.Timestamp("1970-01-01")
        r["solved_time"] = r["solved_time"] + epoch
        # r["team"] = r["team"].apply(str)
        sns.set_style("whitegrid")
        g = sns.displot(
            r,
            x="solved_time",
            stat="count",
            hue=r[
                [
                    "team__in_school_symbol",
                    "team__venue__category__competition",
                    "team__venue__category__identifier",
                ]
            ]
            .apply(tuple, axis=1)
            .apply(lambda x: f"{x[1]} - {x[0]} {x[2]}" if x[0] else f"{x[1]} - {x[2]}"),
            kind="ecdf",
        )
        plt.gcf().set_size_inches(12, 7)

        g.set(
            title=f"Problem solving time Distribution for {self.object}",
            xlabel="Solving time",
            ylabel="Number of teams",
        )

        g.legend.set(
            title="Teams",
        )
        date_form = DateFormatter("%H:%M:%S")
        plt.gca().xaxis.set_major_formatter(date_form)
        plt.xlim(0, None)
        locs, labels = plt.xticks()
        plt.setp(labels, rotation=45, ha="right", rotation_mode="anchor")
        plt.savefig(s, format="svg")
        ctx["plot"] = base64.b64encode(bytes(s.getvalue(), "utf-8")).decode("utf-8")
        return ctx
