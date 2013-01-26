import sys
sys.path.insert(0,'../')
if sys.version_info[:2] == (2,6):
	import unittest2 as unittest
else:
	import unittest
import os
import lean
import shutil
import datetime
import time

from rivets_test import RivetsTest
import rivets

CACHE_PATH = os.path.relpath("../../.sass-cache", __file__)
COMPASS_PATH = os.path.join(RivetsTest.FIXTURE_ROOT, 'compass')
SASS_PATH = os.path.join(RivetsTest.FIXTURE_ROOT, 'sass')

class ScssTemplate(lean.ScssTemplate):
	def sass_options(self):
		scss.LOAD_PATHS += ',%s,%s' % (COMPASS_PATH,SASS_PATH)
		options = self._options
		options.update({
			'filename':self.eval_file(),
			'line':self._line,
			'syntax':'scss',
			'compress':0,
			'load_paths':[COMPASS_PATH,SASS_PATH]
		})
		return options

class TestLeanScss(RivetsTest):

	def setUp(self):
		def get_scss():
			global scss
			import scss

		self.silence_warnings(callback=get_scss)

	def tearDown(self):
		if os.path.exists(CACHE_PATH):
			shutil.rmtree(CACHE_PATH)
		assert not os.path.exists(CACHE_PATH)

	def silence_warnings(self,callback):
		return callback()

	def render(self,path):
		path = self.fixture_path(path)
		def process():
			return ScssTemplate(path).render()
		return self.silence_warnings(callback=process)

	def testProcessVariables(self):
		''' Test process variables '''

		example_css = '''.content-navigation {
  border-color: #3bbfce;
  color: rgb(17.184%, 63.477%, 68.737%);
}
.border {
  padding: 8px;
  margin: 8px;
  border-color: #3bbfce;
}

'''
		self.assertEqual(self.render('sass/variables.scss'),example_css)

	def testProcessNesting(self):
		''' Test process nesting '''

		example_css = '''table.hl {
  margin: 2em 0;
}
table.hl td.ln {
  text-align: right;
}
li {
  font-family: serif;
  font-weight: bold;
  font-size: 1.2em;
}

'''

		self.assertEqual(self.render('sass/nesting.scss'),example_css)

	def testImportScssPartialFromScss(self):
		''' Test @import scss partial from scss '''
		example_css = '''#navbar li {
  border-top-radius: 10px;
  -moz-border-radius-top: 10px;
  -webkit-border-top-radius: 10px;
}
#footer {
  border-top-radius: 5px;
  -moz-border-radius-top: 5px;
  -webkit-border-top-radius: 5px;
}
#sidebar {
  border-left-radius: 8px;
  -moz-border-radius-left: 8px;
  -webkit-border-left-radius: 8px;
}

'''

		self.assertEqual(self.render('sass/import_partial.scss'),example_css)

	def testImportPrefersPartialOverFullName(self):
		''' Test @import prefers partial over fullname '''

		filename = self.fixture_path('sass/test.scss')
		partial = self.fixture_path("sass/_partial.scss")
		other = self.fixture_path("sass/partial.scss")

		def do_test():
			f = open(filename,'w')
			f.write("@import 'partial';")
			f.close()

			f = open(partial,'w')
			f.write(".partial { background: #ff0000; };")
			f.close()

			f = open(other,'w')
			f.write(".partial { background: #0000ff; };")
			f.close()

			self.assertEqual(
					".partial {\n  background: #ff0000;\n}\n\n",
					self.render(filename)
				)

		self.sandbox(filename,partial,other,callback=do_test)

	def testImportCSSFileFromLoadPath(self):
		''' Test @import css file from load path '''

		self.assertEqual(
				'',
				self.render("sass/import_load_path.scss")
			)

	@unittest.skip('Skipping relative imports until supported by pyScss')
	def testImportRelativeFile(self):
		''' Test @import relative file'''

		example_css = '''#navbar li {
  border-top-radius: 10px;
  -moz-border-radius-top: 10px;
  -webkit-border-top-radius: 10px;
}
#footer {
  border-top-radius: 5px;
  -moz-border-radius-top: 5px;
  -webkit-border-top-radius: 5px;
}
#sidebar {
  border-left-radius: 8px;
  -moz-border-radius-left: 8px;
  -webkit-border-left-radius: 8px;
}

'''
		self.assertEqual(
				self.render('sass/shared/relative.scss'),
				example_css
			)

	@unittest.skip('Skipping relative imports until supported by pyScss')
	def testImportRelativeNestedFile(self):
		''' Test import relative nested file '''

		example_css = '''body {
  background: #666666;
}
'''
		self.assertEqual(self.render('sass/relative.scss'),example_css)

	def testModifyFileCausesItToRecompile(self):
		''' Test modify file causes it to recompile '''

		filename = self.fixture_path('sass/test.scss')

		def do_test():
			f = open(filename,'w')
			f.write("body { background: red; };")
			f.close()

			self.assertEqual("body {\n  background: #ff0000;\n}\n\n",self.render(filename))

			f = open(filename,'w')
			f.write("body { background: blue; };")
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(filename,(new_time,new_time))

			self.assertEqual("body {\n  background: #0000ff;\n}\n\n",self.render(filename))

		self.sandbox(filename,callback=do_test)

	@unittest.skip('Skipping until python scss can support custom importers')
	def testModifyPartialCausesItToRecompile(self):
		''' Test modify partial causes it to recompile '''

		filename = self.fixture_path('sass/test.scss')
		partial = self.fixture_path('sass/_partial.scss')

		def do_test():
			f = open(filename,'w')
			f.write("@import 'partial'")
			f.close()

			f = open(partial,'w')
			f.write("body { background: red; };")
			f.close()

			self.assertEqual("body {\n  background: #ff0000;\n}\n\n",self.render(filename))

			f = open(partial,'w')
			f.write("body { background: blue; };")
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(partial,(new_time,new_time))

			self.assertEqual("body {\n  background: #0000ff;\n}\n\n",self.render(filename))

		self.sandbox(filename,partial,callback=do_test)

	def testReferenceImportedVariable(self):
		''' Test reference @import'd variable '''

		self.assertEqual(
				self.render('sass/links.scss'),
				'a:link {\n  color: "#ff0000";\n}\n\n'
			)

	def testImportReferenceVariable(self):
		''' Test @import reference variable '''

		self.assertEqual(
				self.render('sass/main.scss'),
				'#header {\n  color: #0000ff;\n}\n\n'
			)

class TestRivetsSass(TestLeanScss):

	def setUp(self):
		super(TestRivetsSass,self).setUp()

		self.env = rivets.Environment('.')
		self.env.cache = {}
		self.env.append_path(
				self.fixture_path('.'),
				self.fixture_path('compass')
			)

	def teardown(self):
		assert not os.path.exists(CACHE_PATH)

	def render(self,path):
		path = self.fixture_path(path)

		return self.silence_warnings(callback=lambda :str(self.env[path]))


if __name__ == '__main__':
    unittest.main()