
import sys, json
from typing import List, Dict
from datetime import datetime
from Logger import Logger
import uuid # for task unique ID generation


class TaskTracker:

    ACTION_KEY_LIST = "list"
    ACTION_KEY_LIST_DONE = "done"
    ACTION_KEY_LIST_IN_PROGRESS = "in-progress"
    ACTION_KEY_LIST_TODO = "todo"

    ACTION_KEY_ADD = "add"
    ACTION_KEY_UPD = "update"
    ACTION_KEY_DEL = "delete"

    ACTION_KEY_MRK = "mark"

    def __init__(self, config: Dict, arguments = None):
        if not config:
            raise ValueError("Provided config is empty!")
        self.config = config
        self.logger = Logger(config)
        self.init_arguments(arguments)

        self.actions = []

    # === CORE ===

    def get_cli_argument(self, arg_index: int):
        return sys.argv[arg_index]


    def init_arguments(self, arguments: str):
        if arguments:
            self.args = arguments
        else:
            self.args = sys.argv


    def write_the_tasks(self, tasks: List, filename: str=""):
        # EDGE CASES: verify the input
        file = ""
        if filename:
            file = filename
        else:
            file = self.config["file_to_write"]

        with open(file, "w") as f:
            json.dump({"tasks": tasks}, f, indent=3)


    def read_the_tasks(self, status: str="all", read_from_dataset: bool = False, dataset = None) -> List:
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
        if status != "all":
            return [t for t in tasks if t["status"] == status]
        return tasks
    

    def run(self):
        try:
            self.parseArguments()
        except ValueError as e:
            print(e)
        
        for a in self.actions:
            self.run_action(a)
     

    def is_valid(self) -> bool:
        return bool(self.config)
    
    # === ADD ACTION ===

    def add_LIST_action(self, arg_index: int):
        action = self.ACTION_KEY_LIST
        total_arguments = len(sys.argv)
        task_categories = self.config["actions_template"]["list"]

        # case: when we want to list everything
        if arg_index == total_arguments - 1:
            self.actions.append([action, "all"])
            return arg_index + 1
        
        # case: when we want to list a particular category of tasks
        if self.get_cli_argument(arg_index + 1) not in task_categories:
            raise ValueError(action.upper() + self.config["errors"]["incorrectly_specified"])
        
        self.actions.append([action, self.get_cli_argument(arg_index + 1)])
        return arg_index + 2


    def add_ADD_action(self, arg_index: int):
        # Adding a new task
        # task-cli add "Buy groceries"

        action = self.ACTION_KEY_ADD
        total_arguments = len(sys.argv)

        # ADD action MUST be followed by an argument AND the argument must be a string
        if arg_index + 1 >= total_arguments or not isinstance(sys.argv[arg_index + 1], str):
            raise ValueError(action.upper() + self.config["errors"]["incorrectly_specified"])
        
        self.actions.append([action, sys.argv[arg_index + 1]])
        return arg_index + 2


    def add_UPD_action(self, arg_index: int):
        # Updating and deleting tasks | Deleting tasks
        # task-cli update 1 "Buy groceries and cook dinner"

        action = self.ACTION_KEY_UPD
        total_arguments = len(sys.argv)
        # UPDATE action MUST be followed by two arguments
        if arg_index + 2 >= total_arguments:
            raise ValueError(action.upper() + self.config["errors"]["incorrectly_specified"])
        
        id, new_desc = sys.argv[arg_index + 1], sys.argv[arg_index + 2]

        # CHECK if id exists in the tasks
        tasks_id = self.get_task_by_id(id)
        if tasks_id == None:
            raise ValueError(self.config["errors"]["upd_no_id"])
        
        self.actions.append([action, tasks_id, new_desc])

        return arg_index + 3


    def add_DEL_action(self, arg_index: int):
        # task-cli delete 1
        action = self.ACTION_KEY_DEL

        total_arguments = len(sys.argv)
        # UPDATE action MUST be followed by two arguments
        if arg_index + 1 >= total_arguments:
            raise ValueError(action.upper() + self.config["errors"]["incorrectly_specified"])
        
        id = sys.argv[arg_index + 1]

        # CHECK if id exists in the tasks
        tasks_id = self.get_task_by_id(id)
        if tasks_id == None:
            raise ValueError(self.config["errors"]["del_no_id"])
        
        self.actions.append([action, tasks_id])

        return arg_index + 3


    def get_task_by_id(self, id: str) -> int:
        tasks = self.read_the_tasks()

        for i, t in enumerate(tasks):
            if t["id"] == id:
                return i
        return None


    def add_MRK_action(self, arg_index: int):
        # Marking a task as in progress or done
        # task-cli mark-in-progress 1
        # task-cli mark-done 1
        total_arguments = len(sys.argv)
        action = self.ACTION_KEY_MRK

        if sys.argv[arg_index] not in self.config["actions_template"]["mark"]:
            raise ValueError(action.upper() + self.config["errors"]["incorrectly_specified"])
        
        if arg_index + 1 >= total_arguments:
            raise ValueError(action.upper() + self.config["errors"]["incorrectly_specified"])
        
        mark_type, id = self.get_cli_argument(arg_index), self.get_cli_argument(arg_index + 1)
        task_id = self.get_task_by_id(id)
        if task_id  == None:
            raise ValueError(self.config["errors"]["mark_no_id"])        

        self.actions.append([action, task_id, mark_type])
        return arg_index + 2


    def set_action(self, arg_index):
        if arg_index < 1:
            raise ValueError("Incorrect argument index to set action!")
        arg = sys.argv[arg_index].lower()
        
        # LIST
        if arg == self.ACTION_KEY_LIST:
            return self.add_LIST_action(arg_index)
        # ADD
        elif arg == self.ACTION_KEY_ADD:
            return self.add_ADD_action(arg_index)
        # UPDATE 
        elif arg == "update":
            return self.add_UPD_action(arg_index)
        # DELETE
        elif arg == "delete":
            return self.add_DEL_action(arg_index)
        # MARK-IN-PROGRESS | MARK-DONE
        elif "mark-" in arg[0:5]:
            return self.add_MRK_action(arg_index)
        
        raise ValueError(self.config["errors"]["unknown_cmd"])


    def parseArguments(self):
        arguments_num = len(sys.argv)
        if arguments_num < 2:
            raise ValueError("There are no arguments to parse!")
        
        arg_i = 1
        while arg_i < arguments_num:
            arg_i = self.set_action(arg_i)

        self.logger.write("finished parsing", "system")


    # === EXECUTE ACTION ===


    def run_action(self, action):
        named_action = action[0]

        if named_action == TaskTracker.ACTION_KEY_LIST:
            self.list_tasks(action[1])
        elif named_action == TaskTracker.ACTION_KEY_ADD:
            self.add_task(action[1])
        elif named_action == TaskTracker.ACTION_KEY_UPD:
            self.update_task(action[1], action[2])
        elif named_action == TaskTracker.ACTION_KEY_DEL:
            self.delete_task(action[1])
        elif named_action == TaskTracker.ACTION_KEY_MRK:
            self.mark_task(action[1], action[2])


    def list_tasks(self, status: str):
        # EGDE CASES what if the file very long, we'd want to read in batches

        tasks = self.read_the_tasks(status=status)
        
        # CHECK: if there are no tasks found
        if len(tasks) == 0:
            self.logger.write(self.config["messages"]["empty_list"])
            return
        
        self.logger.write(self.config["messages"]["list_of_tasks"].format(status.upper()))
        for t in tasks:
            print(f"{t['id']} | {t['description']} : {t['status']}")


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
        
        tasks.append(new_task)

        self.write_the_tasks(tasks)

        self.logger.write(self.config["messages"]["task_added"].format(new_task['id']))


    def update_task(self, task_id: int, new_desc: str):
        tasks = self.read_the_tasks()
        tasks[task_id]["description"] = new_desc

        self.write_the_tasks(tasks)

        self.logger.write(self.config["messages"]["task_updated"].format(tasks[task_id]["id"]))


    def delete_task(self, task_id: int):
        tasks = self.read_the_tasks()

        exceprt_length = self.config["exceprt_len"]
        task_excerpt = tasks[task_id]["description"][:exceprt_length]

        del tasks[task_id]

        self.logger.write(self.config["messages"]["task_deleted"].format(task_excerpt))
        self.write_the_tasks(tasks)


    def mark_task(self, task_id: int, mark_type: str):
        tasks = self.read_the_tasks()
        
        status = mark_type.split("mark-")[1]
        tasks[task_id]["status"] = status

        exceprt_length = self.config["exceprt_len"]
        excerpt = tasks[task_id]["description"][:exceprt_length]

        self.logger.write(self.config["messages"]["task_marked"].format(excerpt, status.upper()))

        self.write_the_tasks(tasks)

