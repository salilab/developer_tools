#!/usr/bin/env python
import glob
from optparse import OptionParser
import subprocess
import fnmatch
import os
import sys
import multiprocessing
from Queue import Queue
from threading import Thread
import autopep8
import distutils.spawn

sys.path.append(os.path.split(sys.argv[0]))
import python_tools


parser = OptionParser()
parser.add_option("-c", "--clang-format", dest="clang_format",
                  default="auto",
                  help="The clang-format command.")
parser.add_option("-a", "--autopep8", dest="autopep8",
                  default="auto",
                  help="The autopep8 command.")
parser.add_option("-e", "--exclude", dest="exclude",
                  default="eigen3:config_templates",
                  help="Color separated list of dirnames to ignore.")
(options, args) = parser.parse_args()

# clang-format-3.4",
# autopep8

# search for executables
if options.clang_format == "auto":
    options.clang_format = None
    for name in ["clang-format-3.4", "clang-format"]:
        if distutils.spawn.find_executable(name):
            options.clang_format = name
            break
if options.autopep8 == "auto":
    options.autopep8 = None
    for name in ["autopep8"]:
        if distutils.spawn.find_executable(name):
            options.autopep8 = name
            break

exclude = options.exclude.split(":")

error = None


class _Worker(Thread):

    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print e
                error = str(e)
            self.tasks.task_done()


class ThreadPool:

    """Pool of threads consuming tasks from a queue"""

    def __init__(self, num_threads=-1):
        if num_threads == -1:
            num_threads = 2 * multiprocessing.cpu_count()
        print "Creating thread pool with", num_threads
        self.tasks = Queue(-1)
        for _ in range(num_threads):
            _Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        #func(*args, **kargs)
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
        return error


def _do_get_files(glb, cur):
    matches = []
    dirs = []
    for n in os.listdir(cur):
        if n in exclude:
            continue
        name = os.path.join(cur, n)
        if os.path.isdir(name):
            if not os.path.exists(os.path.join(name, ".git")):
                matches += _do_get_files(glb, name)
        elif name.endswith(glb):
            matches.append(name)
    return matches


def _get_files(glb):
    match = []
    if len(args) == 0:
        match = _do_get_files(glb, ".")
    else:
        for a in args:
            if os.path.isdir(a):
                match += _do_get_files(glb, a)
            elif a.endswith(glb):
                match.append(a)
    return match


def _run(cmd):
    # print " ".join(cmd)
    pro = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    output, error = pro.communicate()
    if pro.returncode != 0:
        print " ".join(cmd)
        raise RuntimeError("error running " + error)
    return output


def clean_cpp(path):
    if options.clang_format:
        contents = _run([options.clang_format, "--style=Google", path])
    else:
        contents = open(path, "r").read()
    contents = contents.replace("% template", "%template")
    python_tools.rewrite(path, contents)


def clean_py(path):
    if options.autopep8:
        contents = _run([options.autopep8, "--aggressive", "--aggressive",
                         "--ignore=E24,W602", path])
    else:
        contents = open(path, "r").read()
    if contents.find("# \\example") != -1:
        contents = "#" + contents
    python_tools.rewrite(path, contents)


def main():
    if options.autopep8 is None:
        print "autopep8 not found"
    else:
        print "autopep8 is `%s`" % options.autopep8
    if options.clang_format is None:
        print "clang-format not found"
    else:
        print "clang-format is `%s`" % options.clang_format

    tp = ThreadPool()

    for f in _get_files(".py"):
        # print f
        tp.add_task(clean_py, f)

    for f in _get_files(".h") + _get_files(".cpp"):
        # print f
        tp.add_task(clean_cpp, f)
    tp.wait_completion()

if __name__ == '__main__':
    main()
