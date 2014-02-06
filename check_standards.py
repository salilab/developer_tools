#!/usr/bin/env python

"""Print out any violations of IMP-specific standards. These are things that
   are not fixed by cleanup-code.py."""

import sys
import os.path
import glob
import re
import traceback
import python_tools
try:
    import python_tools.cpp_format as cpp_format
except ImportError:
    cpp_format = None
    print "Cannot conduct additional C++ format checks without the Python "
    print "Pygments (http://pygments.org/) library: please install."
    print

from optparse import OptionParser

parser = OptionParser()
(options, args) = parser.parse_args()


def _check_do_not_commit(line, filename, num, errors):
    marker = 'DO NOT' + ' COMMIT'
    if line.find(marker) >= 0:
        errors.append('%s:%d: Line contains the string "%s"'
                      % (filename, num + 1, marker))


def check_c_file(filename, errors):
    """Check each modified C file to make sure it adheres to the standards"""
    info = python_tools.get_project_info(filename)
    docname = info["name"].replace(".", "/")
    filepath = os.path.split(filename)[0]
    if filepath.find(docname) != -1:
        docname = filepath[filepath.find(docname):]
    elif filepath.find("include") != -1:
        docname = docname + "/" + \
            filepath[filepath.find("include") + len("include"):]
    cppprefix = info["name"].replace(".", "_").upper()
    altcppprefix = info["name"].replace(".", "").upper()
    fh = file(filename, "r").read().split("\n")
    srch = re.compile('\s+$')
    url = re.compile('https?://')
    configh = False
    blank = False
    file_line = False
    exported = filename.find("internal") == - \
        1 and filename.endswith(
            ".h") and filename.find(
            "include") != -1
    name = os.path.split(filename)[1]
    file_line_string = "\\file %s" % (
        "/".join([docname, name])).replace("//", "/")
    for (num, line) in enumerate(fh):
        line = line.rstrip('\r\n')
        if line.find(file_line_string) != -1:
            file_line = True
        # No way to split URLs, so let them exceed 80 characters:
        if line.startswith(">>>>>>> "):
            errors.append(
                "%s:%d: error: Incomplete merge found." %
                (filename, num + 1))
        _check_do_not_commit(line, filename, num, errors)
        if not filename.endswith(".cpp") and line.startswith("#define ") \
           and not line.startswith("#define %s" % cppprefix) \
           and not line.startswith("#define %s" % altcppprefix) \
           and not line.startswith("#define EIGEN_YES_I_KNOW_SPARSE_"
                                   "MODULE_IS_NOT_STABLE_YET"):
            found = False
            fline = line.replace("#define", "#undef")
            for (onum, oline) in enumerate(fh):
                if onum > num and oline.startswith(fline):
                    found = True
            if not found:
                errors.append('%s:%d: error: Preprocessor symbols must start with %s'
                              % (filename, num + 1, cppprefix))
        blank = (len(line) == 0)
        if line.startswith('#include "'):
            configh = True
        if blank and num == 0:
            errors.append('%s:1: File has leading blank line(s)' % filename)
    if exported and filename.endswith(".h") and not file_line:
        # lazy hack with the replace
        errors.append(
            '%s:2: Exported header must have a line  %s' % file_line_string)


def check_python_file(filename, errors):
    """Check each modified Python file to make sure it adheres to the
       standards"""
    temptest = re.compile('\s+def\s+temp_hide_test.*')
    test = re.compile(
        '\s+def\s+(test_[abcdefghijklmnopqrstuvwxyz0123456789_]*)\(')
    import_as = re.compile('[ ]*import [ ]*.* [ ]*as [ ]*.*')
    import_from = re.compile('[ ]*from [ ]*.* [ ]*import [ ]*.*')
    tests = []

    if filename.find("example") != -1:
        is_example = True
    else:
        is_example = False
    for (num, line) in enumerate(file(filename, "r")):
        if num == 0 and is_example:
            if not line.startswith("## "):
                errors.append('%s:%d: Example does not have doxygen comments at start'
                              % (filename, num + 1))
            if line.find("example") == -1:
                errors.append('%s:%d: Example \example marker in first line'
                              % (filename, num + 1))
        _check_do_not_commit(line, filename, num, errors)
        if temptest.match(line):
            errors.append('%s:%d: Test case has the temp_hide_ prefix'
                          % (filename, num + 1))
        m = test.match(line)
        if line.startswith(">>>>>>> "):
            errors.append(
                "%s:%d: error: Incomplete merge found." %
                (filename, num + 1))
        if m:
            g = m.group(1)
            if g in tests:
                errors.append('%s:%d: Test case has multiple tests with the same name %s'
                              % (filename, num + 1, g))
            tests.append(m.group(1))
        if filename.find("test") == -1 and filename.find("example") != -1:
            if import_as.match(line):
                errors.append(
                    '%s:%d: Examples should not rename types on import as that confuses doxygen: ' %
                    (filename, num + 1) + line)
            if import_from.match(line):
                errors.append(
                    '%s:%d: Examples should not use import from as that confuses doxygen: ' %
                    (filename, num + 1) + line)


def get_file(filename):
    return (file(filename, 'r'), filename)


def check_modified_file(filename, errors):
    """Check each modified file to make sure it adheres to the standards"""
    # skip code that isn't ours
    if filename.find("dependency") != -1:
        return
    # don't check header guard in template headers
    if filename.find("templates") != -1:
        return
    info = python_tools.get_project_info(filename)
    if filename.endswith('.h') or filename.endswith('.cpp') \
       or filename.endswith('.c'):
        check_c_file(filename, errors)
        # don't check header guard in template headers
        if cpp_format and filename.endswith('.h') and filename.find("templates") == -1:
            cpp_format.check_header_file(
                get_file(filename),
                info["name"],
                errors)
        elif cpp_format and filename.endswith('.cpp'):
            cpp_format.check_cpp_file(
                get_file(filename),
                info["name"],
                errors)
    elif filename.endswith('.py'):
        check_python_file(filename, errors)


def file_matches_re(pathname, excludes):
    for e in excludes:
        if e.match(pathname):
            return True
    return False


def get_all_files():
    modfiles = []
    excludes = []
    excludes = [re.compile(x) for x in excludes]
    for root, dirs, files in os.walk('.'):
        if '.sconf_temp' not in root and not root.startswith('./build/'):
            for f in files:
                if not f.startswith('.'):
                    pathname = os.path.join(root, f)
                    if not file_matches_re(pathname, excludes):
                        modfiles.append(pathname)
    return modfiles


def main():
    errors = []
    if len(args) == 0:
        modfiles = get_all_files()
        print "usage:", sys.argv[0], "file_patterns"
    else:
        modfiles = args
    for pattern in modfiles:
        expanded = glob.glob(pattern)
        # rint pattern, expanded
        for filename in expanded:
            try:
                check_modified_file(filename, errors)
            except:
                print "Exception processing file " + filename
                traceback.print_exc()
    if len(errors) > 0:
        sys.stderr.write("The following problems needed to be fixed:\n\n")
        sys.stderr.write("\n".join(errors))
        sys.stderr.write("\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
