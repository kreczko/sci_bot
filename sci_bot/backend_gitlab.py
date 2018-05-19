"""Wrapper for python-gitlab."""
import gitlab
import os
import json

from .helpers import cached
from .logger import log
from .backend import EventType

GITLAB_EVENT_TYPE_MAP = dict(
    build=EventType.BUILD,
    pipeline=EventType.CI,
    issue=EventType.ISSUE,
    merge_request=EventType.MERGE_REQUEST,
    note=EventType.NOTE,
    push=EventType.PUSH,
    tag_push=EventType.TAG,
    unknown=EventType.UNKNOWN,
)


class Gitlab(object):
    def __init__(self, repo, auth_token):
        self.repo = repo
        self.auth_token = auth_token
        self.connection = _connect(repo, auth_token)

    def reply_to_issue(self, event, msg):
        project_id = event['project_id']
        issue_iid = event['issue']['iid']

        project = self.connection.projects.get(project_id)
        # get issue from project, direct access (c.issues.get) does not provide
        # access to notes
        issue = project.issues.get(issue_iid)
        self._reply_to_issue(issue, msg)

    def _reply_to_issue(self, issue, msg):
        try:
            issue.notes.create(dict(
                body=msg,
            ))
            issue.save()
        except Exception as e:
            log.error('Unable to reply to issue {}: {}'.format(
                issue.get_id(), e))

    def contains_mention(self, event, name):
        return _contains_mention(event._content, name)


class Event(object):
    def __init__(self, content):
        self._content = content

    @property
    def type(self):
        internal_type = self._get_type()
        if internal_type in GITLAB_EVENT_TYPE_MAP:
            return GITLAB_EVENT_TYPE_MAP[internal_type]
        else:
            return EventType.UNKNOWN

    def _get_type(self):
        if 'object_kind' in self._content:
            return self._content['object_kind']
        else:
            return 'unknown'

    def to_json(self, output_file):
        with open(output_file, 'w') as f:
            json.dump(self._content, f, indent=2)

    def __getitem__(self, key):
        return self._content[key]

    def updated_at(self):
        return self._content['object_attributes']['updated_at']

    @staticmethod
    def from_string(input_string):
        content = json.loads(input_string)
        return Event(content)


@cached('/tmp/projects.pkl')
def get_list_of_projects(connection, get_all=True):
    return connection.projects.list(all=get_all)


def _connect(repo, auth_token):
    connection = gitlab.Gitlab(repo, auth_token, api_version=4)
    connection.auth()
    return connection


@cached('/tmp/mergerequests.pkl')
def get_merge_requests(project, get_all=True):
    mrs = project.mergerequests.list(all=get_all)
    return mrs


def get_merge_request(project, mr_id):
    mr = project.mergerequests.get(mr_id)
    return mr


def add_label_to_merge_request(label, merge_request):
    merge_request.labels.append(label)
    merge_request.save()


def remove_label_from_merge_request(label, merge_request):
    merge_request.labels.remove(label)
    merge_request.save()


def __is_object_kind__(msg, kind):
    return 'object_kind' in msg and msg['object_kind'] == kind


def _contains_mention(msg, mention):
    if 'object_attributes' not in msg:
        return False
    attr = msg['object_attributes']
    note = attr['note']
    return '@' + mention in note


def reply_to(event, msg):
    gitlab_token = os.environ['GIT_ACCESS_TOKEN']

    git_ssh_url = event['project']['git_ssh_url']
    url = url[url.find('@') + 1:url.find(':')]
    url = 'https://{}'.format(url)

    c = connect(url, gitlab_token)

    project_id = event['project_id']
    issue_id = event['issue']['iid']

    project = c.projects.get(project_id)
    # get issue from project, direct access (c.issues.get) does not provide
    # access to notes
    issue = project.issues.get(issue_id)

    issue.notes.create(dict(
        body=msg,
    ))
    issue.save()


def get_note_content(msg):
    return msg['object_attributes']['note']


def get_username(msg):
    return msg['user']['username']


def add_label(issue_id):
    pass


def remove_label(issue_id):
    pass


def trigger_build(project, params):
    project.trigger_build('master', trigger_token,
                          {'extra_var1': 'foo', 'extra_var2': 'bar'})
