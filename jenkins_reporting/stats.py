import collections

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
