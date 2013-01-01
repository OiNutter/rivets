import rivets
env = rivets.Environment()
output = env.compile('test.css')
f = open('compiled.css','w')
f.write(output.encode('utf8'))
f.close()