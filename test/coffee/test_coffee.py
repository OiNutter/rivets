import sys
from os import path
sys.path.insert(0,'../../')

import rivets
env = rivets.Environment()
env.cache = {}
env.append_path(path.dirname(path.abspath( __file__ )))
output = env.compile('foo.js.coffee')
f = open('compiled.js','w')
f.write(output.encode('utf8'))
f.close()