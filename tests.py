from main import configCreate
from typing import Dict, List
from task_tracker_class import TaskTracker
import pytest

# ==== CONFIGURATION ====

def test_create_config_raises_exception_if_configfile_invalid():
    with pytest.raises(FileNotFoundError) as excinfo:
        configCreate("invalid_file")

    assert "Configuration file 'invalid_file' doesn't exist!" in str(excinfo.value)

def test_create_config_valid():
    config = configCreate("config.json")
    assert isinstance(config, Dict)


# ==== TASK TRACKER CLASS ====

# === READ TASKS ===

@pytest.fixture
def tracker() -> TaskTracker:
    return TaskTracker(configCreate("config.json"))

@pytest.fixture
def tasks_dataset() -> object:
    return {"tasks": [
        {
            "id": "1",
            "description": "Description 1",
            "status": "in-progress",
            "createdAt": "now",
            "updatedAt": "now"
        },
        {
            "id": "2",
            "description": "Description 2",
            "status": "todo",
            "createdAt": "now",
            "updatedAt": "now"
        },
        {
            "id": "2",
            "description": "Description 2",
            "status": "done",
            "createdAt": "now",
            "updatedAt": "now"
        },
    ]}

def test_can_read_all_tasks(tracker):
    tasks = tracker.read_the_tasks()
    assert isinstance(tasks, List)
    assert len(tasks) != 0

def test_can_read_tasks_from_dataset(tracker, tasks_dataset):
    tasks = tracker.read_the_tasks(status = "", read_from_dataset = True, dataset = tasks_dataset)

    assert isinstance(tasks, List)
    assert len(tasks) == 3

def test_read_the_tasks_raises_exception_if_dataset_not_provided(tracker):
    with pytest.raises(ValueError) as excinfo:
        tracker.read_the_tasks("", read_from_dataset = True)

    assert "The dataset to read from has not been provided!" in str(excinfo.value)

@pytest.mark.parametrize("task_status, expected_count", [
    ("todo", 1),
    ("in-progress", 1),
    ("done", 1),
])
def test_can_read_tasks_by_status(tracker, task_status, expected_count, tasks_dataset):
    tasks = tracker.read_the_tasks(task_status, read_from_dataset = True, dataset = tasks_dataset)
    
    assert all([task["status"] == task_status for task in tasks])
    assert len(tasks) == expected_count


# === WRITE TASKS ===

def test_can_serialize_generated_task(tracker):
    task = tracker.generate_new_task("new_task")
    print(f"Task: {task}")

    import json
    assert json.dumps(task)
    
def test_can_write_tasks(tracker):
    file_to_write = "test_file.json"
    tasks = [tracker.generate_new_task("new_task")]
    tracker.write_the_tasks(tasks, file_to_write)

    import os, json
    assert os.path.isfile(file_to_write)

    with open(file_to_write, "r") as f:
        contents = json.load(f)
        assert "tasks" in contents
        assert isinstance(contents["tasks"], List)
        assert len(contents["tasks"]) == 1
        assert all(field in contents["tasks"][0] for field in ('id', 'description', 'status', 'createdAt', 'updatedAt'))
    
    os.remove(file_to_write)
    assert not os.path.isfile(file_to_write)

# === SET ACTION ===



# ==== CLI-Level TESTS ====