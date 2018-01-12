import gitlab

from .helpers import cached

@cached('/tmp/projects.pkl')
def get_list_of_projects(connection, getAll=True):
    return connection.projects.list(all=getAll)


def connect(repo, auth_token):
    connection = gitlab.Gitlab(repo, auth_token, api_version=4)
    connection.auth()
    return connection

@cached('/tmp/mergerequests.pkl')
def get_merge_requests(project, getAll=True):
    mrs = project.mergerequests.list(all=getAll)
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