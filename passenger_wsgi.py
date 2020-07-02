# Hornet starts python on python2
# This script starts python within the right venv.
import os
import sys

HOME = "/home/bellettrie"
VENV = HOME + '/test'
PYTHON_BIN = VENV + '/bin/python3'

if sys.executable != PYTHON_BIN:
    os.execl(PYTHON_BIN, PYTHON_BIN, *sys.argv)
sys.path.insert(0, '/home/bellettrie/.local/lib/python3.6/site-packages'.format(v=VENV))

import bellettrie_library_system.wsgi
application = bellettrie_library_system.wsgi.application
