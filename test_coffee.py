import rivets
rivet = rivets.Rivet()
rivet.add_path('test/coffee')
output = rivet.run('test/coffee/foo.js.coffee')
f = open('test/coffee/compiled.js','w')
f.write(output.encode('utf8'))
f.close()