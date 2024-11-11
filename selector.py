#!/usr/bin/env python3

import random
import argparse
import re
from typing import List

HEADER = """--- 
schedulable: true
explicit_sync: true
FPTAS: false
maxRuntime: {sec: 5, nsec: 0}
tasks:"""

def load_task_blocks(file_path: str) -> List[str]:
    """Load task blocks from file, separated by double newlines."""
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            return [block.strip() for block in content.split('\n\n') if block.strip()]
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def select_random_tasks(tasks: List[str], count: int) -> List[str]:
    """Select a specified number of random tasks from the list."""
    if not tasks or count <= 0:
        return []
    return random.sample(tasks, min(count, len(tasks)))

def modify_task_block(task_block: str) -> str:
    """Modify the name and args fields in a task block."""
    # Replace the name field
    task_block = re.sub(r'name: prog', 'name: james', task_block)
    # Replace the args field
    task_block = re.sub(r'args: "0"', 'args: " 4 61428571 2 10"', task_block)
    return task_block

def validate_arguments(args) -> bool:
    """Validate that the sum of task counts doesn't exceed total tasks."""
    specified_sum = args.iso_tasks + args.comb_tasks + args.workload_tasks
    if specified_sum > args.num_tasks:
        print("Error: Sum of specified tasks exceeds total number of tasks")
        return False
    return True

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Select random task configurations from files.')
    parser.add_argument('--num_tasks', type=int, required=True, help='Total number of tasks to select')
    parser.add_argument('--iso_tasks', type=int, required=True, help='Number of isolation tasks')
    parser.add_argument('--comb_tasks', type=int, required=True, help='Number of combination tasks')
    parser.add_argument('--workload_tasks', type=int, required=True, help='Number of workload tasks')
    parser.add_argument('--seed_num', type=int, required=True, help='specifies seed offset: will be appended to file name')
    parser.add_argument('--output', type=str, required=True, help='output file name')

    args = parser.parse_args()
    
    if not validate_arguments(args):
        return

    #set python seed
    random.seed(((args.seed_num + 1) * 2) * ((args.iso_tasks + 1) * 3) * ((args.comb_tasks + 1) * 5) * ((args.workload_tasks + 1) * 7) * ((args.num_tasks + 1) * 11))

    # Load all task files
    task_files = {
        'iso': load_task_blocks('3000s/3000-isofunctional-elastic.yaml'),
        'comb': load_task_blocks('3000s/3000-comb-elastic.yaml'),
        'workload': load_task_blocks('3000s/3000-workload-elastic.yaml'),
        'light': load_task_blocks('3000s/3000-workload-elastic.yaml')
    }

    # Select tasks from each category
    selected_tasks = []
    
    # Add tasks from each category
    selected_tasks.extend(select_random_tasks(task_files['workload'], args.workload_tasks))
    selected_tasks.extend(select_random_tasks(task_files['iso'], args.iso_tasks))
    selected_tasks.extend(select_random_tasks(task_files['comb'], args.comb_tasks))
    
    # Calculate and add light tasks
    specified_sum = args.iso_tasks + args.comb_tasks + args.workload_tasks
    light_tasks_count = args.num_tasks - specified_sum
    selected_tasks.extend(select_random_tasks(task_files['light'], light_tasks_count))

    # Modify each task block
    modified_tasks = [modify_task_block(task) for task in selected_tasks]

    # Write the final configuration to a new file
    output_file = str(args.seed_num) + "_" + args.output
    try:
        with open(output_file, 'w') as f:
            f.write(HEADER + '\n  ')
            f.write('\n\n  '.join(modified_tasks))
        print(f"Successfully wrote {len(modified_tasks)} tasks to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
