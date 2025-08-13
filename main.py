#! /usr/bin/env python3

import sys, json
from typing import List, Dict
from task_tracker_class import TaskTracker

def configCreate(config_filename: str) -> Dict:
    import os
    if not os.path.isfile(config_filename):
        raise FileNotFoundError(f"Configuration file '{config_filename}' doesn't exist!")

    config = {}
    with open(config_filename, "r") as f:
        config = json.load(f)

    return config



def main():
    config: Dict = {}
    try:
        config = configCreate("config.json")
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)

    tracker = TaskTracker(config)    
    if not tracker.is_valid():
        raise ValueError("Tracker is not configured")

    tracker.run()


if __name__ == "__main__":
    main()