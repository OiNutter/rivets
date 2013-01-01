import rivets
env = rivets.Environment()
output = env.compile('foo.js.coffee')
f = open('compiled.js','w')
f.write(output.encode('utf8'))
f.close()