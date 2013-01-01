import rivets
rivet = rivets.Rivet()
rivet.add_path('test/js')
output = rivet.run('test/js/blah.js')
f = open('test/js/compiled.js','w')
f.write(output.encode('utf8'))
f.close()

rivet = rivets.Rivet()
rivet.add_path('test/js')
output = rivet.run('test/js/blah2.js')
f = open('test/js/compiled2.js','w')
f.write(output.encode('utf8'))
f.close()