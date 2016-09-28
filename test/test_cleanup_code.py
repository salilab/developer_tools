import unittest
import subprocess
import os
import utils

TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
cleanup_py = os.path.join(TOPDIR, 'cleanup_code.py')

class Tests(unittest.TestCase):

    def test_all(self):
        """Test cleanup_code script with --all option."""
        with utils.TempDir() as tmpdir:
            pyfile = os.path.join(tmpdir, 'test.py')
            utils.write_file(pyfile, 'def foo():\n  bar\n')
            p = subprocess.Popen([cleanup_py, '--all'], cwd=tmpdir)
            stdout, stderr = p.communicate()
            self.assertEqual(p.returncode, 0)
            # 2-space indentation should have been corrected to 4-space
            self.assertEqual(utils.read_file(pyfile),
                             'def foo():\n    bar\n')

if __name__ == '__main__':
    unittest.main()
