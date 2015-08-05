import collections
from datetime import datetime

from flask import current_app as app

def get_top_by_target(staging_builds):
    counter = collections.defaultdict(int)

    for build in staging_builds:
        for bug in build.get("bugs", []):
            target = bug.get("target")
            if target:
                counter[target] += 1

    return counter


def _match_assignee_to_team(teams, assignee):
        for team, assignees in teams.items():
            if assignee in assignees:
                return team

        return None


def get_top_by_team(staging_builds):
    assignees = []
    teams = app.config["TEAMS"]

    for build in staging_builds:
        for bug in build.get("bugs", []):
            assignee = bug.get("assignee")
            if assignee:
                assignees.append(assignee["name"])

    counter = collections.defaultdict(int)
    for ass in assignees:
        team = _match_assignee_to_team(teams, ass)
        if team:
            counter[team] += 1

    return counter


def _bugs_per_week(failed_builds):
    counter = collections.defaultdict(int)

    for build in failed_builds:
        date = datetime.strptime(build['date'], '%Y-%m-%d')
        (year, week, _) = date.isocalendar()
        key = str(year) + str(week)
        counter[key] += 1

    return counter


def get_basic_stats(all_builds, failed_builds):
    all_cnt = len(all_builds)
    failed_cnt = len(failed_builds)

    teams = app.config["TEAMS"]
    software_failed = []
    infra_failed = []
    for build in failed_builds:
        for bug in build.get('bugs', []):
            if 'assignee' not in bug.keys():
                continue

            assignee = bug['assignee']['name']
            team = _match_assignee_to_team(teams, assignee)

            if team == 'Infra':
                infra_failed.append(build)
            else:
                software_failed.append(build)

    success_ratio = round(1.0 * (all_cnt - failed_cnt) / all_cnt, 2)

    bugs_per_week = _bugs_per_week(failed_builds)
    avg_failed_per_week = failed_cnt/len(bugs_per_week.keys())
    last_week = sorted(bugs_per_week.keys(), reverse=True)[0]
    failed_last_week = bugs_per_week[last_week]

    return {
        "total_builds_num": all_cnt,
        "total_failed_builds_num": failed_cnt,
        "software_failures": len(software_failed),
        "infra_failures": len(infra_failed),
        "success_ratio": success_ratio,
        "avg_failed_per_week": avg_failed_per_week,
        "failed_last_week": failed_last_week
    }
