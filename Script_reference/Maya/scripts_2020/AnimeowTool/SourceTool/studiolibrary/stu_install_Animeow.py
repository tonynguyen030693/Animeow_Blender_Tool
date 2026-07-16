# -----------------------------------
# Studio Library
# www.studiolibrary.com
# -----------------------------------

import os
import sys

Stu_path = os.path.join(os.path.dirname(__file__), "src")
    
if not os.path.exists(Stu_path):
    raise IOError(Stu_path, "does not exist!")
    
if Stu_path not in sys.path:
    sys.path.insert(0, Stu_path)
    
import studiolibrary
studiolibrary.main()
