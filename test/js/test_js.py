import rivets
env = rivets.Environment()
output = env.compile('blah.js')
f = open('compiled.js','w')
f.write(output.encode('utf8'))
f.close()

env = rivets.Environment()
output = env.compile('blah2.js')
f = open('compiled2.js','w')
f.write(output.encode('utf8'))
f.close()