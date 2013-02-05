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

	def testFindMultipleComponentJsonInDirectory(self):
		''' Test find multiple component.json in directory '''

		self.assertEqual(
				'var qunit;\n',
				str(self.env['qunit.js'])
			)

		self.assertEqual(
				'.qunit {}\n',
				str(self.env['qunit.css'])
			)

	def testMissingStaticPathReturnsNone(self):
		''' Test missing static path returns None '''

		self.assertIsNone(self.env[self.fixture_path('default/missing.png')])

	def testFindStaticDirectoryReturnsNone(self):
		''' Test find static directory returns none '''

		self.assertIsNone(self.env['images'])

	def testMissingAssetReturnsNone(self):
		''' Test missing asset returns None '''

		self.assertIsNone(self.env['missing.js'])

	def testMissingAssetPathReturnsNone(self):
		''' Test missing asset path returns None '''

		self.assertIsNone(self.env[self.fixture_path('default/missing.js')])

	def testAssetWithMissingRequiresRaisesAnException(self):
		''' Test asset with missing requires an exception '''

		self.assertRaises(
				rivets.errors.FileNotFound,
				self.env.find_asset,
				'missing_require.js'
			)

	def testAssetWithMissingDependOnRaisesAnException(self):
		''' Test asset with missing depend_on raises an exception '''

		self.assertRaises(
				rivets.errors.FileNotFound,
				self.env.find_asset,
				'missing_depend_on.js'
			)

	def testAssetWithMissingAbsoluteDependOnRaisesAnException(self):
		''' Test asset with missing absolute depend_on raises an exception '''

		self.assertRaises(
				rivets.errors.FileNotFound,
				self.env.find_asset,
				'missing_absolute_depend_on.js'
			)

	def testAssetLogicalPathForAbsolutePath(self):
		''' Test asset logical path for absolute path '''

		self.assertEqual(
				'gallery.js',
				self.env[self.fixture_path("default/gallery.js")].logical_path
			)

		self.assertEqual(
				'application.js',
				self.env[self.fixture_path("default/application.js.coffee")].logical_path
			)

		self.assertEqual(
				'mobile/a.js',
				self.env[self.fixture_path("default/mobile/a.js")].logical_path
			)

	ENTRIES_IN_PATH = 44

	def testIterateOverEachEntry(self):
		''' Test iterate over each entry '''
		entries = []

		def do_test(path):
			print path
			entries.append(path)

		self.env.each_entry(self.fixture_path("default"),do_test)

		self.assertEqual(self.ENTRIES_IN_PATH,len(entries))

	def testEachEntryEnumerator(self):
		''' Test each entry enumerator '''
		enum = self.env.each_entry(self.fixture_path('default'))
		self.assertEqual(self.ENTRIES_IN_PATH,len(enum))

	FILES_IN_PATH = 37

	def testIterateOverEachFile(self):
		''' Test iterate over each file '''

		files = []
		def do_test(filename):
			files.append(filename)

		self.env.each_file(callback=do_test)

		for file in files:
			print file

		self.assertEqual(self.FILES_IN_PATH,len(files))

	def testEachFileEnumerator(self):
		''' Test each file enumerator '''

		enum = self.env.each_file()
		self.assertEqual(self.FILES_IN_PATH,len(enum))

	def testIterateOverEachLogicalPath(self):
		''' Test iterate over each logical path '''

		paths = []
		def do_test(logical_path,filename):
			paths.append(logical_path)

		self.env.each_logical_path(callback=do_test)

		self.assertEqual(self.FILES_IN_PATH,len(paths))
		self.assertEqual(len(paths),len(set(paths)),'Has Duplicates')

		assert 'application.js' in paths
		assert 'coffee/foo.js' in paths
		assert 'coffee/index.js' in paths
		assert not 'coffee' in paths

	def testIterateOverEachLogicalPathAndFilename(self):
		''' Test iterate over each logical path and filename '''

		paths = []
		filenames = []

		def do_test(logical_path,filename):
			paths.append(logical_path)
			filenames.append(filename)

		self.env.each_logical_path(callback=do_test)

		self.assertEqual(self.FILES_IN_PATH,len(paths))
		self.assertEqual(len(paths),len(set(paths)),'Has Duplicates')

		assert 'application.js' in paths
		assert 'coffee/foo.js' in paths
		assert 'coffee/index.js' in paths
		assert not 'coffee' in paths

		match = None
		for p in filenames:
			if re.search(r"""application\.js\.coffee""",p):
				match = p

		assert match

	def testEachLogicalPathEnumerator(self):
		''' Test each logical path enumerator '''

		enum = self.env.each_logical_path()
		self.assertIsInstance(enum[0],str)
		self.assertEqual(self.FILES_IN_PATH,len(list(enum)))

	def testIterateOverEachLogicalPathMatchingFNMatchFilter(self):
		''' Test iterate over each logical path matching fnmatch filters '''

		paths = []

		def do_test(path,filename):
			paths.append(path)

		self.env.each_logical_path('*.js',callback=do_test)

		assert 'application.js' in paths
		assert 'coffee/foo.js' in paths
		assert 'gallery.css' not in paths

	def testIterateOverEachLogicalPathMatchesIndexFiles(self):
		''' Test iterate over each logical path matches index files '''

		paths = []
		def do_test(path,filename):
			paths.append(path)

		self.env.each_logical_path("coffee.js",callback=do_test)

		assert 'coffee.js' in paths
		assert 'coffee/index.js' not in paths

	def testEachLogicalPathEnumeratorMatchingFNMatchFilters(self):
		''' Test each logical path enumerator matching fnmatch filters '''

		paths = []
		enum = self.env.each_logical_path('*.js')
		for logical_path in list(enum):
			paths.append(logical_path)

		assert "application.js" in paths
		assert "coffee/foo.js" in paths
		assert "gallery.css" not in paths

	def testIterateOverEachLogicalPathMatchingRegexpFilters(self):
		''' Test iterate over each logical path matching regexp filters '''

		paths = []
		def do_test(path,filename):
			paths.append(path)

		self.env.each_logical_path(re.compile(r""".*\.js"""),callback=do_test)

		assert "application.js" in paths
		assert "coffee/foo.js" in paths
		assert "gallery.css" not in paths

	def testIterateOverEachLogicalPathMatchingProcFilters(self):
		''' Test iterate over each logical path matching proc filters '''

		paths = []
		def proc(path,fn):
			name,ext = os.path.splitext(path)
			return ext=='.js'

		def do_test(path,filename):
			paths.append(path)

		self.env.each_logical_path(proc,callback=do_test)

		assert "application.js" in paths
		assert "coffee/foo.js" in paths
		assert "gallery.css" not in paths

	def testIterateOverEachLogicalPathMatchingProcFiltersWithFullPathArg(self):
		''' Test iterate over each logical path matching proc filters with full path arg '''

		paths = []
		def proc(path,fn):
			return re.match(re.escape(self.fixture_path('default/mobile')),fn)

		def do_test(path,filename):
			paths.append(path)

		self.env.each_logical_path(proc,callback=do_test)

		assert "mobile/a.js" in paths
		assert "mobile/b.js" in paths
		assert "application.js" not in paths

	def testCoffeeScriptFilesCompiledInClosure(self):
		''' CoffeeScript files are compiled in a closure '''

		script = str(self.env['coffee'])
		import sys
		sys.stdout.write(script)
		import execjs
		self.assertEqual("undefined",execjs.exec_(script))


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

	def testChangingPaths(self):
		''' Test changing paths '''

		self.env.clear_paths()
		self.env.append_path(self.fixture_path('asset'))

	def testRegisterMimeType(self):
		''' Test register mime type '''

		assert not self.env.mimetypes.get_mimetype('jst')
		self.env.register_mimetype('jst','application/javascript')
		self.assertEqual('application/javascript',self.env.mimetypes.get_mimetype('jst'))

	def testRegisterBundleProcessor(self):
		''' Test register bundle processor '''

		assert WhitespaceCompressor not in self.env.processors.get_bundleprocessors('text/css')
		self.env.register_bundleprocessor('text/css',WhitespaceCompressor)
		assert WhitespaceCompressor in self.env.processors.get_bundleprocessors('text/css')

	def testRegisterCompressor(self):
		''' Test register compressor '''

		assert not self.env.processors.get_compressors('text/css').has_key('whitepace')
		self.env.register_compressor('text/css','whitespace',WhitespaceCompressor)
		assert self.env.processors.get_compressors('text/css').has_key('whitespace')

	def testRegisterGlobalBlockPreprocessor(self):
		''' Test register global block preprocessor '''

		old_size = len(self.new_environment().processors.get_preprocessors('text/css'))
		def process(context,data):
			return data
		rivets.processing.processor_registry.register_preprocessor('text/css','foo',callback=process)
		self.assertEqual(old_size+1,len(self.new_environment().processors.get_preprocessors('text/css')))
		rivets.processing.processor_registry.unregister_preprocessor('text/css','foo')
		self.assertEqual(old_size,len(self.new_environment().processors.get_preprocessors('text/css')))

	def testUnregisterCustomBlockPreProcessor(self):
		''' Test unregister global block processor '''

		old_size = len(self.env.processors.get_preprocessors('text/css'))
		def process(context,data):
			return data
		self.env.register_preprocessor('text/css','foo',callback=process)
		self.assertEqual(old_size+1,len(self.env.processors.get_preprocessors('text/css')))
		self.env.unregister_preprocessor('text/css','foo')
		self.assertEqual(old_size,len(self.env.processors.get_preprocessors('text/css')))


if __name__ == '__main__':
    unittest.main()