#!/usr/bin/env python
import sys
import glob
import os
import os.path
import difflib

sys.path.append(os.path.split(sys.argv[0])[0])
import python_tools


def _get_files(ds, suffix):
    ret = []
    for (dirpath, dirnames, filenames) in walk(directory):
        for f in filenames:
            if f.endswith(suffix):
                ret.append(
                    os.path.join(dirpath,
                                 f)[len(ds) + 1:].replace("\\",
                                                          "/"))
    ret.sort()
    return ret


def make_files(d):
    output = os.path.join(d, "Files.cmake")
    cppfiles = _get_files(d, ".cpp")
    pyfiles = _get_files(d, ".py")
    jsonfiles = _get_files(d, ".json")
    out = ["set(pyfiles \"%s\")" % ";".join(pyfiles),
           "set(cppfiles \"%s\")" % ";".join(cppfiles)]
    if len(jsonfiles) > 0:
        out.append("set(jsonfiles \"%s\")" % ";".join(jsonfiles))
    _rewrite(output, out)

directories = sys.argv[1:] if len(sys.argv) > 1 else ['.']
for directory in directories:
    for (dirpath, dirnames, filenames) in walk(directory):
        for d in dirnames:
            if d in ["bin", "src", "test", "examples", "benchmark"]:
                make_files(os.path.join(dirpath, d))
