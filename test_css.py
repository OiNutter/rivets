import rivets
rivet = rivets.Rivet()
rivet.add_path('test/css')
output = rivet.run('test/css/test.css')
f = open('test/css/compiled.css','w')
f.write(output.encode('utf8'))
f.close()