
import sys, json
from typing import List, Dict
from datetime import datetime
import uuid # for task unique ID generation

class TaskTracker:
    ACTION_KEY_LIST = "list"
    ACTION_KEY_LIST_DONE = "done"
    ACTION_KEY_LIST_IN_PROGRESS = "in-progress"
    ACTION_KEY_LIST_TODO = "todo"

    ACTION_KEY_ADD = "add"
    ACTION_KEY_DELETE = "delete"

    def __init__(self, config: Dict):
        self.tasks = []
        self.config = config
        self.actions = []

        self.configureParser()
    
    def set_action(self, arg_index, total_args):
        arg = sys.argv[arg_index]
        list_actions = self.config["actions_template"]["list"]

        # LIST
        if arg == self.ACTION_KEY_LIST:
            if arg_index + 1 >= total_args or sys.argv[arg_index + 1] not in list_actions:
                raise ValueError(f"List action is not specified correctly. Make sure you specify the correct task status '{list_actions}'")
            else:
                self.actions.append([arg, sys.argv[arg_index + 1]])
                return arg_index + 1
        # ADD
        elif arg == self.ACTION_KEY_ADD:
            if arg_index + 1 >= total_args or not isinstance(sys.argv[arg_index + 1], str):
                raise ValueError("Add action is not specified correctly")
            else:
                self.actions.append([arg, sys.argv[arg_index + 1]])
                return arg_index + 1

        # UPDATE
        elif arg == "update":
            pass

        # DELETE
        elif arg == "delete":
            pass

        # MARK-IN-PROGRESS
        elif arg == "mark-in-progress":
            pass

        # MARK-DONE
        elif arg == "mark-done":
            pass

        return arg_index

    def parseArguments(self):
        arguments_n = len(sys.argv)
        if arguments_n < 2:
            return
        
        for arg_i in range(1, arguments_n):
            arg_i = self.set_action(arg_i, arguments_n)


    def configureParser(self):
        if not self.config:
            raise ValueError("Config is not configured")

        try:
            self.parseArguments()
        except ValueError as e:
            print(e)


    def run_action(self, action):
        named_action = action[0]

        if named_action == TaskTracker.ACTION_KEY_LIST:
            self.list_tasks(action[1])
        elif named_action == TaskTracker.ACTION_KEY_ADD:
            self.add_task(action[1])


    def run(self):
        for a in self.actions:
            self.run_action(a)
        
        

    def list_tasks(self, status: str):
        # EGDE CASES what if the file very long, we'd want to read in batches
        print(f"Here's a list of your {status} tasks:")
        tasks = self.read_the_tasks(status=status)

        for t in tasks:
            print(f"{t['id']} - {t['description']} - {t['status']}")

    def generate_new_task(self, description: str) -> object:
        return {
            "id": str(uuid.uuid4()),
            "description": description,
            "status": self.ACTION_KEY_LIST_TODO,
            "createdAt": str(datetime.now()),
            "updatedAt": str(datetime.now())
        }

    def add_task(self, task_desc: str):
        # EDGE CASES what if the task exists?
        # EDGE CASES what is the tasks list is very long, so we don't need to read all the tasks
        tasks = self.read_the_tasks()

        new_task = self.generate_new_task(task_desc)
        
        print(f"Adding new task '{new_task['id']}' : '{new_task['description'][:20]}' to the list!")
        tasks.append(new_task)

        self.write_the_tasks(tasks)
    
    def write_the_tasks(self, tasks: List, filename: str=""):
        # EDGE CASES: verify the input
        file = ""
        if filename:
            file = filename
        else:
            file = self.config["file_to_write"]

        with open(file, "w") as f:
            json.dump({"tasks": tasks}, f, indent=3)


    def read_the_tasks(self, status: str="", read_from_dataset: bool = False, dataset = None) -> List:
        tasks = []

        # read the tasks (either from dataset or json)
        if read_from_dataset:
            if not dataset:
                raise ValueError("The dataset to read from has not been provided!")
            
            tasks = dataset["tasks"]
        else:
            with open(self.config["file_to_read"], "r") as f:
                tasks = [t for t in json.load(f)["tasks"]]                

        # filter by status if needed
        if status:
            return [t for t in tasks if t["status"] == status]
        return tasks
    
    def is_valid(self) -> bool:
        return bool(self.config)
