import rivets
rivet = rivets.Rivet()
rivet.add_path('test/scss')
output = rivet.run('test/scss/test.css.scss')
f = open('test/scss/compiled.css','w')
f.write(output.encode('utf8'))
f.close()