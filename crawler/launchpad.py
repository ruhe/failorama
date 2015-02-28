from crawler import util

BUG_TASKS_URL = "https://api.launchpad.net/1.0/bugs/{0}/bug_tasks"
BUG_URL = "https://api.launchpad.net/1.0/bugs/{0}"


@util.memoize
def get_assignee(link):
    resp = util.get_json(link)
    return util.select_keys(resp, ['display_name', 'name', 'is_team'])


def append_assignee_info(bug):
    link = bug['assignee_link']
    if link:
        bug['assignee'] = get_assignee(link)
        util.remove_key(bug, 'assignee_link')

    return bug


def get_main_bug_task(bug_id):
    url = BUG_TASKS_URL.format(bug_id)
    resp = util.get_json(url)

    task = resp['entries'][0]
    task = util.select_keys(task, ['assignee_link', 'bug_target_name',
                                   'importance', 'status'])
    util.rename_key(task, 'bug_target_name', 'target')
    return task


def append_main_bug_task(bug):
    task = get_main_bug_task(bug['id'])
    bug.update(task)

    return bug


def get_bug_basic_info(link):
    resp = util.get_json(link)
    info = util.select_keys(resp, ['id', 'title', 'duplicate_of_link'])
    return info


def replace_duplicate(bug):
    link = bug['duplicate_of_link']
    if link:
        return get_bug_basic_info(link)
    else:
        return bug


@util.memoize
def get_bug(bug_id):
    try:
        url = BUG_URL.format(bug_id)

        bug = get_bug_basic_info(url)
        bug = replace_duplicate(bug)
        bug = append_main_bug_task(bug)
        bug = append_assignee_info(bug)
        return bug
    except:
        return {'id': bug_id, 'title': 'Unknown'}
