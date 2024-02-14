import pytest
import random
import requests
from tests.task import Task
from datetime import datetime
from typing import List

BASE_URL = "https://todo.pixegami.io"
URL_LIST_TASK = BASE_URL + "/list-tasks/{user_id}"
URL_GET_TASK = BASE_URL + "/get-task/{task_id}"
URL_UPDATE_TASK = BASE_URL + "/update-task"
URL_CREATE_TASK = BASE_URL + "/create-task"
URL_DELETED_TASK = BASE_URL + "/delete-task/{task_id}"


def get_tasks(user_id: str) -> List[Task]:
    url = URL_LIST_TASK.format(user_id=user_id)
    response = requests.get(url=url)
    task_list = response.json()["tasks"]
    return [Task.from_dict(data=task) for task in task_list]


@pytest.mark.parametrize("user_id", ["123"])
def test_retrieve_task_list(user_id: str):
    url = URL_LIST_TASK.format(user_id=user_id)
    response = requests.get(url=url)
    assert response.status_code == 200
    data = response.json()
    task_list = data.get("tasks")
    assert len(task_list) > 0
    tasks = [Task.from_dict(data=task) for task in task_list]
    assert len(tasks) > 0
    first_task = tasks[0]
    assert isinstance(first_task.is_done, bool)
    assert first_task.user_id == "123"
    created_datetime = datetime.fromtimestamp(first_task.created_time)
    assert created_datetime is not None


@pytest.mark.parametrize("user_id", ["123"])
def test_retrieve_task_by_id(user_id: str):
    tasks = get_tasks(user_id=user_id)
    assert len(tasks) > 0
    first_task = tasks[0]
    task_id = first_task.task_id
    url = URL_GET_TASK.format(task_id=task_id)
    response = requests.get(url=url)
    assert response.status_code == 200
    data = response.json()
    task = Task.from_dict(data=data)
    assert task.task_id == task_id
    assert isinstance(task.is_done, bool)
    assert task.user_id == "123"
    created_datetime = datetime.fromtimestamp(task.created_time)
    assert created_datetime is not None


@pytest.mark.parametrize("user_id", ["123"])
def test_update_task(user_id: str):
    tasks = get_tasks(user_id=user_id)
    assert len(tasks) > 0
    first_task = tasks[0]
    task_id = first_task.task_id
    random_string = ("%06x" % random.randrange(16**6)).upper()
    update_data = {"task_id": task_id, "content": random_string}
    response = requests.put(url=URL_UPDATE_TASK, json=update_data)
    assert response.status_code == 200
    assert response.json()["updated_task_id"] == task_id


def test_create_task(delete_after_create_task, request):
    user_id = "123"
    random_string = ("%06x" % random.randrange(16**6)).upper()
    task_data = {
        "is_done": False,
        "content": random_string,
        "user_id": user_id,
    }
    response = requests.put(url=URL_CREATE_TASK, json=task_data)
    assert response.status_code == 200
    assert response.json()["task"] is not None
    task_created = Task.from_dict(data=response.json()["task"])
    assert task_created.task_id.startswith("task_")
    assert task_created.is_done is False
    assert task_created.content == random_string
    assert task_created.user_id == user_id
    ttl_datetime = datetime.fromtimestamp(task_created.ttl)
    present = datetime.now()
    assert present < ttl_datetime
    request.node.task_id = task_created.task_id


@pytest.fixture(scope="function")
def delete_after_create_task(request):
    def cleanup():
        print("--delete task--")
        print(request.node.task_id)
        requests.delete(url=URL_DELETED_TASK.format(task_id=request.node.task_id))

    request.addfinalizer(cleanup)
