import sys
sys.path.insert(0,'../')
import unittest

from lean.coffee import CoffeeScriptTemplate
from rivets_test import RivetsTest
import rivets

class TestAssetAttributes(RivetsTest):

	def pathname(self,path):
		env = rivets.Environment()
		env.append_path(self.fixture_path('default'))
		return env.get_attributes_for(path)

	def test_search_paths(self):
		self.assertEqual(["index.js","index/component.json"],self.pathname("index.js").search_paths())
		self.assertEqual(["foo.js","foo/component.json","foo/index.js"],self.pathname("foo.js").search_paths())
		self.assertEqual(["foo/bar.js","foo/bar/index.js"],self.pathname("foo/bar.js").search_paths())

	def test_logical_path(self):
		self.assertEqual("application.js",self.pathname(self.fixture_path('default/application.js')).get_logical_path())
		self.assertEqual("application.css",self.pathname(self.fixture_path('default/application.css')).get_logical_path())
		self.assertEqual("jquery.foo.min.js",self.pathname(self.fixture_path('default/jquery.foo.min.js')).get_logical_path())

		self.assertEqual("application.js",self.pathname(self.fixture_path("default/application.js.coffee")).get_logical_path())
		self.assertEqual("application.css",self.pathname(self.fixture_path("default/application.css.scss")).get_logical_path())

		self.assertEqual("application.js",self.pathname(self.fixture_path("default/application.coffee")).get_logical_path())
		self.assertEqual("application.css",self.pathname(self.fixture_path("default/application.scss")).get_logical_path())

	def test_extensions(self):
		self.assertEqual([],self.pathname('empty').get_extensions())
		self.assertEqual([".js"],self.pathname('gallery.js').get_extensions())
		self.assertEqual([".js",".coffee"],self.pathname('application.js.coffee').get_extensions())

	def test_format_extension(self):
		self.assertEqual([],self.pathname('empty').get_engine_extensions())
		self.assertEqual([],self.pathname('gallery.js').get_engine_extensions())
		self.assertEqual([".coffee"],self.pathname('application.js.coffee').get_engine_extensions())
		self.assertEqual([],self.pathname('jquery.js').get_engine_extensions())
		self.assertEqual([],self.pathname('jquery.min.js').get_engine_extensions())
		self.assertEqual([],self.pathname('jquery.tmpl.min.js').get_engine_extensions())
		self.assertEqual([".coffee"],self.pathname('jquery.min.coffee').get_engine_extensions())

		env = rivets.Environment()
		env.register_engine('.ms',object())
		self.assertEqual([".ms"],env.get_attributes_for("foo.ms").get_engine_extensions())

	def test_content_type(self):
		self.assertEqual("application/octet-stream",self.pathname("empty").get_content_type())
		self.assertEqual("application/javascript",self.pathname("gallery.js").get_content_type())
		self.assertEqual("application/javascript",self.pathname("application.js.coffee").get_content_type())
		self.assertEqual("application/javascript",self.pathname("project.js.coffee.erb").get_content_type())
		self.assertEqual("text/css",self.pathname("gallery.css.erb").get_content_type())
		self.assertEqual("application/javascript",self.pathname("jquery.tmpl.min.js").get_content_type())

		if hasattr(CoffeeScriptTemplate,'default_mime_type'):
			self.assertEqual("application/javascript",self.pathname('application.coffee').get_content_type())

if __name__ == '__main__':
    unittest.main()