import sys
sys.path.insert(0,'../')
import unittest
import os
import lean
import shutil

from rivets_test import RivetsTest
import rivets

CACHE_PATH = os.path.relpath("../../.sass-cache", __file__)
COMPASS_PATH = os.path.join(RivetsTest.FIXTURE_ROOT, 'compass')
SASS_PATH = os.path.join(RivetsTest.FIXTURE_ROOT, 'sass')

class ScssTemplate(lean.ScssTemplate):
	def sass_options(self):
		scss.LOAD_PATHS = COMPASS_PATH + ',test/fixtures/sass' 
		options = self._options
		options.update({
			'filename':self.eval_file(),
			'line':self._line,
			'syntax':'scss',
			'compress':0
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

	
if __name__ == '__main__':
    unittest.main()