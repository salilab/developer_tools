#!/usr/bin/env python
"""Make a header that lists other headers.
usage: make_all_header.py header_name.h include_prefix headers
"""

import sys
import glob
import os

sys.path.append(os.path.split(sys.argv[0])[0])
import python_tools

includepath = sys.argv[1][sys.argv[1].find("include") + len("include") + 1:]

output = ["""/**
 *  \\file %s
 *  \\brief A container which has pairs which ensure a set is connected
 *
 *  Copyright 2007-2013 IMP Inventors. All rights reserved.
 */
""" % includepath]
guard = includepath.replace(
    "/",
    "_").replace("\\",
                 "_").replace(".",
                              "_").upper()
output.append("#ifndef %s" % guard)
output.append("#define %s" % guard)

for h in sys.argv[3:]:
    pat = os.path.join(h, "*.h")
    allh = sorted(glob.glob(pat))
    for g in allh:
        name = os.path.split(g)[1]
        output.append("#include <%s/" % sys.argv[2] + name + ">")

output.append("#endif /* %s */" % guard)
python_tools.rewrite(sys.argv[1], "\n".join(output))
