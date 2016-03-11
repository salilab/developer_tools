import unittest
import subprocess
import os
import shutil
import tempfile

TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
replace_py = os.path.join(TOPDIR, 'replace.py')

class TempDir(object):
    def __enter__(self):
        self.__tmpdir = tempfile.mkdtemp()
        return self.__tmpdir
    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.__tmpdir, ignore_errors=True)

def write_file(fname, content):
    with open(fname, "w") as fh:
        fh.write(content)

def read_file(fname):
    with open(fname, "r") as fh:
        return fh.read()

class Tests(unittest.TestCase):

    def test_replace(self):
        """Test replace.py script"""
        with TempDir() as tmpdir:
            filenames = [os.path.join(tmpdir, x) for x in ['a', 'b', 'c']]
            os.mkdir(filenames[0])
            write_file(filenames[1], "foo bar baz")
            write_file(filenames[2], "bar baz")
            p = subprocess.Popen([replace_py, 'foo', 'bar'] + filenames,
                                 cwd=tmpdir)
            stdout, stderr = p.communicate()
            self.assertEqual(p.returncode, 0)
            self.assertEqual(read_file(filenames[1]), "bar bar baz")
            self.assertEqual(read_file(filenames[2]), "bar baz")

    def test_replace_usage(self):
        """Test replace.py script usage"""
        p = subprocess.Popen([replace_py])
        stdout, stderr = p.communicate()
        self.assertEqual(p.returncode, 1)

if __name__ == '__main__':
    unittest.main()
