#coding=utf8

"""
Usage:
  test.py [-h|-v|-a]
  test.py clear
  test.py (<id> [done|undone|remove])|<task>...

Options:
  -h --help      show this message
  -v --version   show version
  -a --all       show all

Examples:
  Add a task                    todo Go shopping!
  Check a task as done          todo 1 done
  Check a task as undone        todo 1 undne
  Print all tasks               todo --all
  Print undone tasks            todo
"""


from models import Task
from models import Todo
from models import TaskNotFound
from parser import parser
from generator import generator
from version import __version__

from os.path import join
from os.path import exists
from os.path import expanduser
from termcolor import colored
from docopt import docopt


class TodoApp(object):
    """
    Todo cli application.
    """

    def __init__(self):
        self.todo = self.parse_from_file()

    def file_path(self):
        """
          todo will use ./todo.txt prior to ~/todo.txt for persistent storage.
        """
        fn = "todo.txt"
        home_fn = join(expanduser("~"), fn)
        open(home_fn, "a").close()  # touch if not exists

        if exists(fn):
            return fn
        else:
            return home_fn

    def parse_from_file(self):
        """
        Read todos from file.
        return the tasks of "todo.txt".
        """
        content = open(self.file_path()).read()
        return parser.parse(content)

    def generate_to_file(self):
        """
        Generate tasks to file.
        """
        content = generator.generate(self.todo)
        open(self.file_path(), "w").write(content)

    def print_task(self, task):
        """
        Print single task to terminal.
        """
        status = colored('✓', 'green') if task.done else colored('✖', 'red')
        print str(task.id) + '.' + ' ' + status + '  ' + task.content

    def print_task_by_id(self, id):
        """
        Print single task by its id.
        """
        self.print_task(self.todo[id])

    def ls_tasks(self):
        """
        ls all tasks ouput to screen.
        """
        for task in self.todo:
            self.print_task(task)

    def ls_undone_tasks(self):
        """
        ls all undone tasks
        """
        for task in self.todo:
            if not task.done:
                self.print_task(task)

    def check_task(self, id):
        """
        Check one task to done.
        """
        self.todo.check_task(id)
        self.generate_to_file()

    def undo_task(self, id):
        """
        Check one task to undone.
        """
        self.todo.undo_task(id)
        self.generate_to_file()

    def clear_tasks(self):
        """
        Clear todo!
        """
        self.todo.clear()
        self.generate_to_file()

    def add_task(self, content):
        """
        Add new task.
        """
        self.todo.new_task(content)
        self.generate_to_file()

    def remove_task(self, task_id):
        """
        Remove task from todo by its id
        """
        task = self.todo[task_id]
        self.todo.remove(task)
        self.generate_to_file()

    def run(self):
        """
        Get arguments from cli and run!
        """

        args = docopt(__doc__, version="Version: " + __version__)

        if args["clear"]:
            self.clear_tasks()
        elif args["<id>"]:
            try:
                id = int(args["<id>"])
                if args["done"]:
                    self.check_task(id)
                elif args["undone"]:
                    self.undo_task(id)
                elif args["remove"]:
                    self.remove_task(id)
                else:
                    self.print_task_by_id(id)
            except ValueError:
                # if not an integer format str, use as a task
                self.add_task(args["<id>"])
            except TaskNotFound:
                print colored("Task Not Found.", "red")
        elif args["<task>"]:
            self.add_task(" ".join(args["<task>"]))
        elif args["--all"]:
            self.ls_tasks()
        else:
            self.ls_undone_tasks()


def main():
    """
    Run todo cli script.
    """
    app = TodoApp()
    app.run()


if __name__ == '__main__':
    main()
