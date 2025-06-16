import argparse
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / 'todo_data.json'


def load_tasks():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def add_task(description):
    tasks = load_tasks()
    task_id = tasks[-1]['id'] + 1 if tasks else 1
    tasks.append({'id': task_id, 'desc': description, 'done': False})
    save_tasks(tasks)
    print(f"Added task {task_id}: {description}")


def list_tasks(show_all=False):
    tasks = load_tasks()
    for t in tasks:
        if show_all or not t['done']:
            status = '✔' if t['done'] else '✗'
            print(f"{t['id']}: [{status}] {t['desc']}")


def mark_done(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t['id'] == task_id:
            t['done'] = True
            save_tasks(tasks)
            print(f"Task {task_id} marked as done")
            return
    print(f"Task {task_id} not found")


def delete_task(task_id):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t['id'] != task_id]
    if len(new_tasks) == len(tasks):
        print(f"Task {task_id} not found")
    else:
        save_tasks(new_tasks)
        print(f"Task {task_id} deleted")


def main():
    parser = argparse.ArgumentParser(description='Simple CLI TODO app')
    subparsers = parser.add_subparsers(dest='command')

    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('desc', help='Task description')

    parser_list = subparsers.add_parser('list', help='List tasks')
    parser_list.add_argument('-a', '--all', action='store_true', help='Show all tasks including done')

    parser_done = subparsers.add_parser('done', help='Mark task as done')
    parser_done.add_argument('id', type=int, help='Task ID')

    parser_del = subparsers.add_parser('del', help='Delete a task')
    parser_del.add_argument('id', type=int, help='Task ID')

    args = parser.parse_args()

    if args.command == 'add':
        add_task(args.desc)
    elif args.command == 'list':
        list_tasks(args.all)
    elif args.command == 'done':
        mark_done(args.id)
    elif args.command == 'del':
        delete_task(args.id)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
