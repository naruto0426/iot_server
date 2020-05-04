import glob
import re
from os.path import dirname, basename, isfile, join
models = glob.glob(join('app/models', "*.py"))
for model in models:
  exec('from ' + re.sub(r'/|\\','.',model)[:-3] + ' import *')