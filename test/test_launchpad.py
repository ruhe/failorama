import mock
from crawler import launchpad as lp
from crawler import util

import base


def basic_info(id=100):
    return {
        'id': id,
        'title': 'Fake title',
        'duplicate_of_link': None
    }


def basic_info_dup(id=101):
    return {
        'id': id,
        'title': 'Fake title',
        'duplicate_of_link': 'fake_duplicate_link'
    }


def assignee():
    return {
        'display_name': 'Springfield Isotopes',
        'name': 'isotopes',
        'is_team': True
    }


def main_task():
    return {
        'entries': [
            {
                'status': 'New',
                'importance': 'Critical',
                'bug_target_name': 'MOS',
                'assignee_link': 'https://fake_link'
            }]
    }


class TestLaunchpad(base.TestCase):

    @mock.patch('crawler.util.get_json', return_value=basic_info())
    def test_get_bug_basic_info(self, mock_get_json):
        info = lp.get_bug_basic_info('fake_url')
        self.assertDictContainsSubset(basic_info(), info)

        mock_get_json.assert_called_with('fake_url')

    @mock.patch('crawler.util.get_json', return_value=basic_info())
    def test_replace_dubplicate_bug(self, mock_get_json):
        lp.replace_duplicate(basic_info_dup())
        mock_get_json.assert_called_with('fake_duplicate_link')

    @mock.patch('crawler.util.get_json', return_value=assignee())
    def test_get_assignee(self, _):
        info = lp.get_assignee('fake_link')
        self.assertDictContainsSubset(assignee(), info)

    @mock.patch('crawler.util.get_json', return_value=assignee())
    def test_append_assignee_info(self, _):
        bug = {'assignee_link': 'random', 'id': 102}
        info = lp.append_assignee_info(bug)

        self.assertDictContainsSubset(assignee(), info['assignee'])

    @mock.patch('crawler.util.get_json', return_value=main_task())
    def test_get_main_task(self, mock_get_json):
        bug_id = 103
        info = lp.get_main_bug_task(bug_id)
        expected = main_task()['entries'][0]
        util.rename_key(expected, 'bug_target_name', 'target')
        self.assertDictContainsSubset(expected, info)

        mock_get_json.assert_called_with(lp.BUG_TASKS_URL.format(bug_id))

    @mock.patch('crawler.util.get_json', return_value=main_task())
    def test_append_main_task(self, mock_get_json):
        bug = basic_info()
        bug = lp.append_main_bug_task(bug)

        expected = main_task()['entries'][0]
        util.remove_key(expected, 'bug_target_name')
        self.assertDictContainsSubset(expected, bug)
        mock_get_json.assert_called_with(lp.BUG_TASKS_URL.format(bug['id']))

    @mock.patch('crawler.util.get_json',
                side_effect=[basic_info(), main_task(), assignee()])
    def test_get_bug(self, mock_get_json):
        bug_id = 104
        info = lp.get_bug(bug_id)
        self.assertDictContainsSubset(basic_info(), info)
        self.assertDictContainsSubset(assignee(), info['assignee'])

        self.assertEqual('New', info['status'])
        self.assertEqual('Critical', info['importance'])
        self.assertEqual('MOS', info['target'])

        mock_get_json.assert_any_call(lp.BUG_URL.format(bug_id))

        mocked_bug_id = basic_info()['id']
        mock_get_json.assert_any_call(lp.BUG_TASKS_URL.format(mocked_bug_id))

        mock_get_json.assert_any_call('https://fake_link')
