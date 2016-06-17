"""
Change
======

Manage gerrit changes
"""

from gerrit.helper import decode_json
from gerrit.error import UnhandledError
from gerrit.projects.project import Project

def add_change(gerrit_con, project, subject, branch, options):
    """
    Create a change
    :param gerrit_con: Gerrit connection
    :type gerrit_con: gerrit.Gerrit
    :param project: Project to create change in
    :type project: str or gerrit.project.Project
    :param subject: Subject of the change
    :type subject: str
    :param branch: The name of the target branch
    :type branch: str
    :param options: Additional options
    :type options: Dict
    """

    r_endpoint = "/a/changes/"

    if isinstance(project, Project):
        project = project.name

    data = {
        'project': project,
        'subject': subject,
        'branch': branch,
    }

    if options is None:
        options = {}

    for key in options.keys():
        data[key] = options[key]

    req = gerrit_con.call(
        request='post',
        r_endpoint=r_endpoint,
        r_payload=data,
    )

    result = req.content.decode('utf-8')

    if req.status_code == 201:
        return Change(gerrit_con,
                      project,
                      branch,
                      decode_json(result).get('change_id')
                     )
    else:
        raise UnhandledError(result)

class Change(object):
    """Manage gerrit changes"""

    def __init__(self, gerrit_con, project, branch, change_id):
        """
        :param project: Project that contains change
        :type project: str or gerrit.projects.Project
        :param change_id: ID of change
        :type change_id: str
        :param branch: Branch change exists in
        :type branch: str
        """

        if isinstance(project, Project):
            project = project.name

        if project == '':
            raise KeyError('Project required')

        if branch == '':
            raise KeyError('Branch required')

        if change_id == '':
            raise KeyError('Id required')

        # HTTP REST API HEADERS
        self._change_id = '%s~%s~%s' % (project, branch, change_id)
        self._gerrit_con = gerrit_con

        change_info = self._get_change()
        self.full_id = change_info.get('id')
        self.project = change_info.get('project')
        self.branch = change_info.get('branch')
        self.change_id = change_info.get('change_id')
        self.subject = change_info.get('subject')
        self.status = change_info.get('status')
        self.created = change_info.get('created')
        self.updated = change_info.get('updated')
        self.mergable = change_info.get('mergable')
        self.insertions = change_info.get('insertions')
        self.deletions = change_info.get('deletions')
        self.number = change_info.get('number')
        self.owner = change_info.get('owner')

    def _get_change(self):
        """
        Get ChangeInfo for a change
        :returns: Dict of the ChangeInfo for the change
        :rtype: dict
        :exception: ValueError, UnhandledError
        """
        r_endpoint = "/a/changes/%s/" % self._change_id

        req = self._gerrit_con.call(r_endpoint=r_endpoint)

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if status_code == 200:
            return decode_json(result)
        elif status_code == 404:
            raise ValueError(result)
        else:
            raise UnhandledError(result)
