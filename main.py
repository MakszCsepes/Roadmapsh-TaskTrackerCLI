#! /usr/bin/env python3

import argparse
import json
import sys
from typing import List, Dict

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
                raise ValueError("List action is not specified correctly")
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


    def add_task(self, task: str):
        # EDGE CASES what if the task exists?
        tasks = self.read_the_tasks()
        
        new_task = {
            "id": "100", # TODO generate ID
            "description": task,
            "status": self.ACTION_KEY_LIST_TODO,
            "createdAt": "now", # TODO generate the date
            "updatedAt": "now"  # TODO generate the date
        }

        tasks.append(new_task)

        self.write_the_tasks(tasks)
    
    def write_the_tasks(self, tasks):
        # EDGE CASES: verify the input


        with open(self.config["file_to_write"], "w") as f:
            json.dump({"tasks": tasks}, f, indent=3)


    def read_the_tasks(self, status: str="") -> List:
        tasks = []
        
        # read the tasks from the json file
        with open(self.config["file_to_write"], "r") as f:
            if status:
                tasks = [t for t in json.load(f)["tasks"] if t["status"] == status]
            else:
                tasks = [t for t in json.load(f)["tasks"]]
        return tasks

def main():
    config = {}
    with open("config.json", "r") as f:
        config = json.load(f)

    tracker = TaskTracker(config)
    
    if not tracker:
        raise ValueError("Tracker is not configured")

    tracker.run()




if __name__ == "__main__":
    main()