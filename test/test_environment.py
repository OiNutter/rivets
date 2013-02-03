import sys
sys.path.insert(0,'../')
if sys.version_info[:2] == (2,6):
	import unittest2 as unittest
else:
	import unittest
import os
import re

from rivets_test import RivetsTest
import rivets

class EnvironmentTests(object):

	def testWorkingDirectoryIsDefaultRoot(self):
		''' Test working directory is the default root '''

		self.assertEqual(os.path.realpath(os.curdir),self.env.root)

	def testActiveCSSCompressor(self):
		''' Test active css compressor '''

		self.assertIsNone(self.env.processors.css_compressor)

	def testActiveJSCompressor(self):
		''' Test active js compressor '''

		self.assertIsNone(self.env.processors.js_compressor)

	def testPaths(self):
		''' Test paths '''

		self.assertEqual(
				[self.fixture_path("default")],
				list(self.env.paths)
			)

	def testRegisterGlobalPath(self):
		''' Test register global path '''
		self.assertEqual(
				[self.fixture_path('default')],
				list(self.new_environment().paths)
			)

		rivets.path_registry.append_path(self.fixture_path('asset'))

		self.assertEqual(
				[self.fixture_path("asset"),self.fixture_path('default')],
				list(self.new_environment().paths)
			)

		rivets.path_registry.clear_paths()

	def testExtensions(self):
		''' Test extensions '''

		for ext in ['coffee','scss','str','mako']:
			assert ".%s"%ext in self.env.engines.engine_extensions

		for ext in ['js','css']:
			assert not ".%s"%ext in self.env.engines.engine_extensions

	def testFormatExtensions(self):
		''' Test format extensions '''

		for ext in ['js','css']:
			assert ".%s"%ext in self.env.format_extensions

		for ext in ['coffee','scss','str','mako']:
			assert not ".%s"%ext in self.env.format_extensions

	def testAssetDataURIHelper(self):
		''' Test asset_data_uri helper '''
		asset = self.env["with_data_uri.css"]
		self.assertEqual(
				"body {\n  background-image: url(data:image/gif;base64,R0lGODlhAQABAIAAAP%2F%2F%2FwAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw%3D%3D) no-repeat;\n}\n",
				str(asset)
			)

	def testLookupMimeType(self):
		''' Test lookup mime type '''
		self.assertEqual("application/javascript",self.env.mimetypes.get_mimetype(".js"))
		self.assertEqual("application/javascript",self.env.mimetypes.get_mimetype("js"))
		self.assertEqual("text/css",self.env.mimetypes.get_mimetype(".css"))
		self.assertEqual(None,self.env.mimetypes.get_mimetype("foo"))
		self.assertEqual(None,self.env.mimetypes.get_mimetype("foo"))

	def testLookupBundleProcessors(self):
		''' Test lookup bundle processors '''

		self.assertEqual([],self.env.processors.get_bundleprocessors('application/javascript'))
		self.assertEqual(
				[rivets.processing.CharsetNormalizer],
				self.env.processors.get_bundleprocessors('text/css')
			)

	def testLookupCompressors(self):
		''' Test lookup comrpessors '''

		self.assertEqual(
				rivets.processing.CSSMinCompressor,
				self.env.processors.get_compressors('text/css')['cssmin']
			)

		self.assertEqual(
				rivets.processing.UglipyJSCompressor,
				self.env.processors.get_compressors('application/javascript')['uglify']	
			)

	def testResolveInEnvironment(self):
		''' Test resolve in environment '''

		self.assertEqual(
				self.fixture_path('default/gallery.js'),
				self.env.resolve('gallery.js')
			)

		self.assertEqual(
				self.fixture_path('default/coffee/foo.coffee'),
				self.env.resolve("coffee/foo.js")
			)

	def testMissingFileRaisesAnException(self):
		''' Test missing file raises an exception '''

		self.assertRaises(
				rivets.errors.FileNotFound,
				self.env.resolve,
				'null'
			)

	def testFindBundleAssetInEnvironment(self):
		''' Test find bundled asset in environment '''

		self.assertEqual(
				"var Gallery = {};\n",
				str(self.env['gallery.js'])
			)

	def testFindBundledAssetWithAbsolutePathEnvironment(self):
		''' Test find bundled asset with absolute path environment '''

		self.assertEqual(
				"var Gallery = {};\n",
				str(self.env[self.fixture_path('default/gallery.js')])
			)

	def testFindBundledAssetWithImplicitFormat(self):
		''' Test find bundled asset with implicit format '''

		self.assertEqual(
				"(function() {\n  var foo;\n\n  foo = 'hello';\n\n}).call(this);\n",
				str(self.env['coffee/foo.js'])
			)

	def testFindStaticAssetInEnvironment(self):
		''' Test find static asset in environment '''

		self.assertEqual(
					'Hello world\n',
					str(self.env['hello.txt'])
			)

	def testFindStaticAssetWithLeadingSlashInEnvironment(self):
		''' Test find static asset with leading slash in environment '''

		self.assertEqual(
				"Hello world\n",
				str(self.env[self.fixture_path('default/hello.txt')])
			)

	def testFindIndexJSInDirectory(self):
		''' Test find index.js in directory '''

		self.assertEqual(
				"var A;\nvar B;\n",
				str(self.env['mobile.js'])
			)

	def testFindIndexCssInDirectory(self):
		''' Test index.css in directory '''

		self.assertEqual(
				".c {}\n.d {}\n/*\n\n */\n\n",
				str(self.env['mobile.css'])
			)

	def testFindComponentJsonInDirectory(self):
		''' Test find component.json in directory '''
		
		self.assertEqual(
				'var bower;\n',
				str(self.env['bower.js'])
			)

class WhitespaceCompressor(object):

	def compress(self,source):
		return re.sub(r"""\s+""","",self.source)

class TestEnvironment(RivetsTest,EnvironmentTests):

	def new_environment(self,callback=None):
		env = rivets.Environment('.')
		env.append_path(self.fixture_path('default'))
		env.cache = {}
		return callback(env) if callback else env

	def setUp(self):
		self.env = self.new_environment()

if __name__ == '__main__':
    unittest.main()