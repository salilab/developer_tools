import tempfile
import shutil

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
