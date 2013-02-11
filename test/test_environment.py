import sys
sys.path.insert(0,'../')
if sys.version_info[:2] == (2,6):
	import unittest2 as unittest
else:
	import unittest
import os
import re
import datetime,time

from rivets_test import RivetsTest
import rivets
import execjs
import lean

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
		self.assertEqual("application/javascript",self.env.mimetypes[".js"])
		self.assertEqual("application/javascript",self.env.mimetypes["js"])
		self.assertEqual("text/css",self.env.mimetypes[".css"])
		self.assertEqual(None,self.env.mimetypes["foo"])
		self.assertEqual(None,self.env.mimetypes["foo"])

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

		assert not self.env.mimetypes['jst']
		self.env.register_mimetype('jst','application/javascript')
		self.assertEqual('application/javascript',self.env.mimetypes['jst'])

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

	def testUnregisterCustomBlockPreprocessor(self):
		''' Test unregister global block preprocessor '''

		old_size = len(self.env.processors.get_preprocessors('text/css'))
		def process(context,data):
			return data
		self.env.register_preprocessor('text/css','foo',callback=process)
		self.assertEqual(old_size+1,len(self.env.processors.get_preprocessors('text/css')))
		self.env.unregister_preprocessor('text/css','foo')
		self.assertEqual(old_size,len(self.env.processors.get_preprocessors('text/css')))

	def testRegisterGlobalBlockPostprocessor(self):
		''' Test register global block postprocessor '''

		old_size = len(self.new_environment().processors.get_postprocessors('text/css'))
		def process(context,data):
			return data
		rivets.processing.processor_registry.register_postprocessor('text/css','foo',callback=process)
		self.assertEqual(old_size+1,len(self.new_environment().processors.get_postprocessors('text/css')))
		rivets.processing.processor_registry.unregister_postprocessor('text/css','foo')
		self.assertEqual(old_size,len(self.new_environment().processors.get_postprocessors('text/css')))

	def testUnregisterCustomBlockPostprocessor(self):
		''' Test unregister global block postprocessor '''

		old_size = len(self.env.processors.get_postprocessors('text/css'))
		def process(context,data):
			return data
		self.env.register_postprocessor('text/css','foo',callback=process)
		self.assertEqual(old_size+1,len(self.env.processors.get_postprocessors('text/css')))
		self.env.unregister_postprocessor('text/css','foo')
		self.assertEqual(old_size,len(self.env.processors.get_postprocessors('text/css')))

	def testUnregisterCustomBlockBundleProcessor(self):
		''' Test unregister global block bundle processor '''

		old_size = len(self.env.processors.get_bundleprocessors('text/css'))
		def process(context,data):
			return data
		self.env.register_bundleprocessor('text/css','foo',callback=process)
		self.assertEqual(old_size+1,len(self.env.processors.get_bundleprocessors('text/css')))
		self.env.unregister_bundleprocessor('text/css','foo')
		self.assertEqual(old_size,len(self.env.processors.get_bundleprocessors('text/css')))
	
	def testRegisterGlobalBundleProcessor(self):
		''' Test register global bundle processor '''

		assert WhitespaceCompressor not in self.env.processors.get_bundleprocessors('text/css')
		rivets.processing.processor_registry.register_bundleprocessor('text/css',WhitespaceCompressor)
		env = self.new_environment()
		assert WhitespaceCompressor in env.processors.get_bundleprocessors('text/css')
		rivets.processing.processor_registry.unregister_bundleprocessor('text/css',WhitespaceCompressor)

	def testSettingCSSCompressorToNoneClearsCurrentCompressor(self):
		''' Test setting css compressor to None clears current compressor '''

		self.env.css_compressor = WhitespaceCompressor
		assert self.env.css_compressor
		self.env.css_compressor = None
		self.assertIsNone(self.env.css_compressor)
		
	def testSettingJSCompressorToNoneClearsCurrentCompressor(self):
		''' Test setting js compressor to None clears current compressor '''

		self.env.js_compressor = WhitespaceCompressor
		assert self.env.js_compressor
		self.env.js_compressor = None
		self.assertIsNone(self.env.js_compressor)

	def testSettingJSCompressorToLeanHandler(self):
		''' Test setting js compressor to Lean handler '''

		self.assertIsNone(self.env.js_compressor)
		self.env.js_compressor = rivets.processing.UglipyJSCompressor
		self.assertEqual(rivets.processing.UglipyJSCompressor,self.env.js_compressor)
		self.env.js_compressor = None
		self.assertIsNone(self.env.js_compressor)

	def testSettingCSSCompressorToLeanHandler(self):
		''' Test setting css compressor to Lean handler '''

		self.assertIsNone(self.env.css_compressor)
		self.env.css_compressor = rivets.processing.CSSMinCompressor
		self.assertEqual(rivets.processing.CSSMinCompressor,self.env.css_compressor)
		self.env.css_compressor = None
		self.assertIsNone(self.env.css_compressor)

	def testSettingJSCompressorToString(self):
		''' Test setting js compressor to string '''

		self.assertIsNone(self.env.js_compressor)
		self.env.js_compressor = 'uglifier'
		self.assertEqual(rivets.processing.UglipyJSCompressor,self.env.js_compressor)
		self.env.js_compressor = None
		self.assertIsNone(self.env.js_compressor)

	def testSettingCSSCompressorToString(self):
		''' Test setting css compressor to string '''

		self.assertIsNone(self.env.css_compressor)
		self.env.css_compressor = 'cssmin'
		self.assertEqual(rivets.processing.CSSMinCompressor,self.env.css_compressor)
		self.env.css_compressor = None
		self.assertIsNone(self.env.css_compressor)

	def testChangingDigestImplementationClass(self):
		''' Test changing digest implementation class '''

		old_digest = self.env.digest.hexdigest()
		old_asset_digest = self.env['gallery.js'].digest

		import hashlib

		self.env.digest_class = hashlib.sha1

		self.assertNotEqual(old_digest,self.env.digest.hexdigest())
		self.assertNotEqual(old_asset_digest,self.env['gallery.js'].digest)

	def testChangingDigestVersion(self):
		''' Test changing digest version '''
		old_digest = self.env.digest.hexdigest()
		old_asset_digest = self.env['gallery.js'].digest

		self.env.version = 'v2'

		self.assertNotEqual(old_digest,self.env.digest.hexdigest())
		self.assertNotEqual(old_asset_digest,self.env['gallery.js'].digest)

	def testBundledAssetIsStaleIfItsMTimeIsUpdatedorDeleted(self):
		''' Test bundled asset is stale if its mtime is updated or deleted ''' 

		filename = os.path.join(self.fixture_path('default'),"tmp.js")

		def do_test():
			self.assertIsNone(self.env['tmp.js'])

			f = open(filename,'w')
			f.write('foo;')
			f.close()
			self.assertEqual('foo;\n',str(self.env['tmp.js']))

			f = open(filename,'w')
			f.write('bar;')
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(filename,(new_time,new_time))
			self.assertEqual("bar;\n",str(self.env['tmp.js']))

			os.unlink(filename)
			self.assertIsNone(self.env['tmp.js'])

		self.sandbox(filename,callback=do_test)

	def testStaticAssetIsStaleIfItsMTimeIsUpdatedorDeleted(self):
		''' Test static asset is stale if its mtime is updated or deleted ''' 

		filename = os.path.join(self.fixture_path('default'),"tmp.png")

		def do_test():
			self.assertIsNone(self.env['tmp.png'])

			f = open(filename,'w')
			f.write('foo;')
			f.close()
			self.assertEqual('foo;',str(self.env['tmp.png']))

			f = open(filename,'w')
			f.write('bar;')
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(filename,(new_time,new_time))
			self.assertEqual("bar;",str(self.env['tmp.png']))

			os.unlink(filename)
			self.assertIsNone(self.env['tmp.png'])

		self.sandbox(filename,callback=do_test)

	def testBundledAssetCachedIfTheresAnErrorBuildingIt(self):
		''' Test bundled asset cached if there's an error building it '''

		self.env.cache = None

		filename = os.path.join(self.fixture_path('default'),'tmp.coffee')

		def do_test():
			f = open(filename,'w')
			f.write('-->')
			f.close()
			self.assertRaises(
					execjs.ProgramError,
					self.env.find_asset,
					'tmp.js'
				)

			f = open(filename,'w')
			f.write('->')
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(filename,(new_time,new_time))
			self.assertEqual("(function() {\n\n  (function() {});\n\n}).call(this);\n",str(self.env['tmp.js']))

		self.sandbox(filename,callback=do_test)

	def testSeperateContextsClassesForEachInstance(self):
		''' Test seperate contexts classes for each instance '''

		e1 = self.new_environment()
		e2 = self.new_environment()

		self.assertRaises(
				AttributeError,
				getattr,
				e1.context_class,
				'foo'
			)

		self.assertRaises(
				AttributeError,
				getattr,
				e2.context_class,
				'foo'
			)

		def foo(self):
			pass

		def bind_method(func,klass):
			import new
			method = new.instancemethod(func,None,klass)
			setattr(klass,	func.__name__,method)

		bind_method(foo,e1.context_class)
		assert getattr(e1.context_class,'foo')
		self.assertRaises(
				AttributeError,
				getattr,
				e2.context_class,
				'foo'
			)

	def testRegisteringEngineAddsToTheEnvironmentsExtensions(self):
		''' Test registering engine adds to the environments extensions '''

		assert not self.env.engines['.foo']
		assert ".foo" not in self.env.extensions

		self.env.register_engine('.foo',lean.StringTemplate)

		assert self.env.engines['.foo']
		assert ".foo" in self.env.extensions

	def testSeperateEnginesForEachInstance(self):
		''' Test seperate engines for each instance '''

		e1 = self.new_environment()
		e2 = self.new_environment()

		self.assertIsNone(e1.engines['.foo'])
		self.assertIsNone(e2.engines['.foo'])

		e1.register_engine('.foo',lean.StringTemplate)

		assert e1.engines['.foo']
		self.assertIsNone(e2.engines['foo'])

	def testDisablingDefaultDirectiveProcessor(self):
		''' Test disabling default directive processor '''

		self.env.unregister_preprocessor('application/javascript',rivets.processing.DirectiveProcessor)
		self.assertEqual(
				"// =require \"notfound\"\n;\n", 
				str(self.env["missing_require.js"])
			)

class TestIndex(RivetsTest,EnvironmentTests):

	def new_environment(self,callback=None):
		env = rivets.Environment('.')
		env.append_path(self.fixture_path('default'))
		env.cache = {}
		return callback(env).index if callback else env.index

	def setUp(self):
		self.env = self.new_environment()

	def testDoesNotAllowNewMimeTypesToBeAdded(self):
		''' Test does not allow new mime types to be added '''
		self.assertRaises(
				TypeError,
				self.env.register_mimetype,
				".jst",
				"application/javascript"
			)

	def testChangeInEnvironmentMimeTypesDoesNotAffectIndex(self):
		''' Test change in environment mime types does not affect index '''

		env = rivets.Environment('.')
		env.register_mimetype('.jst','application/javascript')
		index = env.index

		self.assertEqual('application/javascript',index.mimetypes['.jst'])
		env.register_mimetype(".jst",None)
		self.assertEqual('application/javascript',index.mimetypes['.jst'])

	def testDoesNotAllowBundleProcessorsToBeAdded(self):
		''' Test does not allow bundle processors to be added '''

		self.assertRaises(
				TypeError,
				self.env.register_bundleprocessor,
				'text/css',
				WhitespaceCompressor
			)

	def testDoesNotAllowBundleProcessorsToBeRemoved(self):
		''' Test does not allow bundle processors to be removed '''

		self.assertRaises(
				TypeError,
				self.env.unregister_bundleprocessor,
				'text/css',
				WhitespaceCompressor
			)

	def testChangeInEnvironmentBundleProcessorsDoesNotAffectIndex(self):
		''' Test change in environment bundle processors does not affect index '''

		env = rivets.Environment('.')
		index = env.index

		assert WhitespaceCompressor not in index.processors.get_bundleprocessors('text/css')
		env.register_bundleprocessor('text/css',WhitespaceCompressor)
		assert WhitespaceCompressor not in index.processors.get_bundleprocessors('text/css')

	def testDoesNotAllowJSCompressorToBeChanged(self):
		''' Test does not allow JS compressor to be changed '''

		self.assertRaises(
				TypeError,
				self.env.js_compressor,
				WhitespaceCompressor
			)

	def testDoesNotAllowCSSCompressorToBeChanged(self):
		''' Test does not allow CSS compressor to be changed '''

		self.assertRaises(
				TypeError,
				self.env.css_compressor,
				WhitespaceCompressor
			)	

	def testChangeInEnvironmentEnginesDoesNotAffectIndex(self):
		''' Test change in environment engines does not affect index '''

		env = rivets.Environment('.')
		index = env.index

		self.assertIsNone(env.engines['.foo'])
		self.assertIsNone(index.engines['.foo'])

		env.register_engine('.foo',lean.StringTemplate)
		
		assert env.engines['.foo']
		self.assertIsNone(index.engines['.foo'])

if __name__ == '__main__':
    unittest.main()