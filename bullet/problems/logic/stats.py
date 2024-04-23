from collections import defaultdict
from datetime import timedelta

from competitions.models import Category, Competition
from django_rq import job
from users.models import Team

from problems.models import ProblemStat, SolvedProblem


@job
def generate_stats(competition: Competition | int):
    if isinstance(competition, int):
        competition = Competition.objects.get(id=competition)

    for category in competition.category_set.all():
        ProblemStat.objects.filter(team__venue__category=category).delete()
        generate_stats_category(category)


def generate_stats_category(category: Category):
    category_problems = category.problems.all()
    first_problem = category.first_problem
    problem_number_map: dict[int, int] = {
        p.problem.id: p.number for p in category_problems
    }
    problem_id_map: dict[int, int] = {p.number: p.problem.id for p in category_problems}

    solves = SolvedProblem.objects.filter(team__venue__category=category).order_by(
        "competition_time"
    )
    teams = Team.objects.filter(id__in=solves.values("team"))

    # dict[team_id][problem_number] = receive/solve time
    receive_times: dict[int, dict[int, timedelta]] = defaultdict(lambda: {})
    solve_times: dict[int, dict[int, timedelta]] = defaultdict(lambda: {})

    # Populate receive times with first problems
    for team in teams:
        receive_times[team.id] = {
            i + first_problem: timedelta(seconds=0)
            for i in range(category.problems_per_team)
        }

    for solve in solves:
        solve_times[solve.team_id][
            problem_number_map[solve.problem_id]
        ] = solve.competition_time

        # The team just received their next problem
        received_problem = len(receive_times[solve.team_id]) + first_problem
        receive_times[solve.team_id][received_problem] = solve.competition_time

    stats = []
    for team in teams:
        for number, received in receive_times[team.id].items():
            if number > len(category_problems):
                continue
            solved = None
            if number in solve_times[team.id]:
                solved = solve_times[team.id][number]

            stat = ProblemStat(
                team=team,
                problem_id=problem_id_map[number],
                received_time=received,
                solved_time=solved,
                solve_duration=solved - received if solved else None,
            )
            stats.append(stat)

    ProblemStat.objects.bulk_create(stats)
