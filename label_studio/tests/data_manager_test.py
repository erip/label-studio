import pytest

# label_studio
from label_studio import blueprint as server
from label_studio.tests.base import goc_project


@pytest.fixture(autouse=True)
def default_project(monkeypatch):
    """
        apply patch for
        label_studio.server.project_get_or_create()
        for all tests.
    """
    monkeypatch.setattr(server, 'project_get_or_create', goc_project)


def project_init_source():
    project = goc_project()
    ids = range(0, 16)
    values = [{'image': '123', 'text': '123'}] * 16
    project.source_storage.remove_all()
    project.source_storage.set_many(ids, values)
    return project


def project_init_target():
    project = goc_project()
    ids = range(0, 16)
    project.target_storage.remove_all()
    for i in ids:
        value = {'text': '123', 'completions': [{'id': 1001 + i}]}
        project.target_storage.set(i, value)
    return project


class TestColumns:
    """ Table Columns
    """
    def test_import_page(self, test_client, captured_templates):
        response = test_client.get('/api/project/columns')
        assert response.status_code == 200


class TestTabs:
    """ Table Tabs
    """
    def test_tabs(self, test_client, captured_templates):
        response = test_client.get('/api/project/tabs')
        assert response.status_code == 200

    def test_selected_items(self, test_client, captured_templates):
        project_init_source()

        # post
        response = test_client.post('/api/project/tabs/1/selected-items', json=[1, 2, 3])
        assert response.status_code == 201

        # get
        response = test_client.get('/api/project/tabs/1/selected-items')
        assert response.status_code == 200
        assert response.json == [1, 2, 3]

        # patch
        response = test_client.patch('/api/project/tabs/1/selected-items', json=[4, 5])
        assert response.status_code == 201
        response = test_client.get('/api/project/tabs/1/selected-items')
        assert response.status_code == 200
        assert response.json == [1, 2, 3, 4, 5]

        # delete
        response = test_client.delete('/api/project/tabs/1/selected-items', json=[3])
        assert response.status_code == 204
        response = test_client.get('/api/project/tabs/1/selected-items')
        assert response.status_code == 200
        assert response.json == [1, 2, 4, 5]

        # check tab has selectedItems
        response = test_client.get('/api/project/tabs/1/')
        assert response.status_code == 200
        assert response.json['selectedItems'] == [1, 2, 4, 5]

        # select all
        response = test_client.post('/api/project/tabs/1/selected-items', json='all')
        assert response.status_code == 201
        response = test_client.get('/api/project/tabs/1/selected-items')
        assert response.status_code == 200
        assert response.json == list(range(0, 16))

        # delete all
        response = test_client.delete('/api/project/tabs/1/selected-items', json='all')
        assert response.status_code == 204
        response = test_client.get('/api/project/tabs/1/selected-items')
        assert response.status_code == 200
        assert response.json == []


class TestActions:

    def test_get_actions(self, test_client, captured_templates):
        # GET: check action list
        response = test_client.get('/api/project/actions')
        assert response.status_code == 200
        assert response.json == [{'id': 'delete_tasks', 'order': 100, 'title': 'Delete tasks'},
                                 {'id': 'delete_completions', 'order': 101, 'title': 'Delete completions'}]

    def test_action_tasks_delete(self, test_client, captured_templates):
        """ Remove tasks by ids
        """
        project = project_init_source()

        # POST: delete 3 tasks
        before_task_ids = set(project.source_storage.ids())
        items = [4, 5, 6]
        response = test_client.post('/api/project/tabs/1/selected-items', json=items)
        assert response.status_code == 201
        response = test_client.post('/api/project/tabs/1/actions?id=delete_tasks')
        assert response.status_code == 200
        after_task_ids = set(project.source_storage.ids())
        assert before_task_ids - set(items) == after_task_ids, 'Tasks after deletion are incorrect'

    def test_action_tasks_completions_delete(self, test_client, captured_templates):
        """ Remove all completions for task ids
        """
        project = project_init_target()

        """# POST: delete 3 tasks
        before_ids = set(project.target_storage.ids())
        items = [4, 5, 6]
        response = test_client.post('/api/project/tabs/1/selected-items', json=items)
        assert response.status_code == 201
        response = test_client.post('/api/project/tabs/1/actions?id=delete_tasks_completions')
        assert response.status_code == 200
        after_ids = set(project.source_storage.ids())
        assert before_ids - set(items) == after_ids, 'Completions after deletion are incorrect'"""


class TestTasksAndAnnotations:
    """ Test tasks on tabs
    """
    def test_tasks(self, test_client, captured_templates):
        response = test_client.get('/api/project/tabs/1/tasks')
        assert response.status_code == 200

    def test_annotations(self, test_client, captured_templates):
        response = test_client.get('/api/project/tabs/1/annotations')
        assert response.status_code == 200