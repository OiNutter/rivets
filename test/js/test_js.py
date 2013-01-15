import sys
from os import path
sys.path.insert(0,'../../')

import rivets
env = rivets.Environment()
env.cache = rivets.caching.FileStore('./tmp')
env.append_path(path.dirname(path.abspath( __file__ )))
output = env.compile('blah.js')
f = open('compiled.js','w')
f.write(output.encode('utf8'))
f.close()

env = rivets.Environment()
env.append_path(path.dirname(path.abspath( __file__ )))
output = env.compile('blah2.js')
f = open('compiled2.js','w')
f.write(output.encode('utf8'))
f.close()