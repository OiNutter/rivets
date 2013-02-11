import sys
sys.path.insert(0,'../')
if sys.version_info[:2] == (2,6):
	import unittest2 as unittest
else:
	import unittest
import os
import time,datetime
import regex as re

from lean import CoffeeScriptTemplate

from rivets_test import RivetsTest
import rivets

class AssetTests(object):

	def testPathnameExists(self):
		''' Test pathname exists'''

		assert os.path.exists(self.asset.pathname)

	def testMtime(self):
		''' Test mtime '''

		assert self.asset.mtime

	def testDigestIsSourceDigest(self):
		''' Test digest is source digest '''

		digest = self.env.digest
		digest.update(str(self.asset))

		self.assertEqual(
				digest.hexdigest(),
				self.asset.digest
			)

	def testLengthIsSourceLength(self):
		''' Test length is source length '''

		self.assertEqual(
				len(str(self.asset)),
				self.asset.length
			)

	def testStale(self):
		''' Test stale? '''
		assert not self.asset.is_stale(self.env)

	def testFresh(self):
		''' Test fresh? '''
		assert self.asset.is_fresh(self.env)

	def testDependenciesAreAList(self):
		''' Test dependencies are a list '''
		self.assertIsInstance(self.asset.dependencies,list)

	def testSplatAsset(self):
		''' Test splat asset '''
		self.assertIsInstance(self.asset.to_list(),list)

	def testBodyIsAString(self):
		''' Test body is a string '''
		self.assertIsInstance(self.asset.body,str)

	def testToListBodyPartsEqualsToStr(self):
		''' Test to_list body parts equal to_string '''
		source = ""
		for asset in self.asset.to_list():
			source += asset.body

		self.assertEqual(str(self.asset),source)

	def testWriteToFile(self):
		''' Test write to file '''
		target = self.fixture_path('asset/tmp.js')
		def do_test():
			self.asset.write_to(target)
			assert os.path.exists(target)
			self.assertEqual(self.asset.mtime,os.stat(target).st_mtime)

		self.sandbox(target,callback=do_test)

	def testWriteToGzippedFile(self):
		''' Test write to gzipped file '''

		target = self.fixture_path('asset/tmp.js.gz')

		def do_test():
			self.asset.write_to(target)
			assert os.path.exists(target)
			self.assertEqual(self.asset.mtime,os.stat(target).st_mtime)

		self.sandbox(target,callback=do_test)

class FreshnessTests(object):

	def testAssetIsStaleWhenItsContentsHaveChanged(self):
		''' Test asset is stale when its contents have changed '''

		filename = self.fixture_path('asset/test.js')

		def do_test():
			f = open(filename,'w')
			f.write("a;")
			f.close()

			asset = self.get_asset("test.js")

			assert asset.is_fresh(self.env)

			f = open(filename,'w')
			f.write("b;")
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(filename,(new_time,new_time))

			assert asset.is_stale(self.env)

		self.sandbox(filename,callback=do_test)

	def testAssetIsStaleIfFileRemoved(self):
		''' Test asset is stale if the file is removed '''
		filename = self.fixture_path('asset/test.js')

		def do_test():
			f = open(filename,'w')
			f.write("a;")
			f.close()

			asset = self.get_asset("test.js")

			assert asset.is_fresh(self.env)

			os.unlink(filename)

			assert asset.is_stale(self.env)

		self.sandbox(filename,callback=do_test)

	def testAssetIsStaleWhenSourceFileModified(self):
		''' Test asset is stale when one of it's source files is modified '''

		main = self.fixture_path('asset/test-main.js')
		dep = self.fixture_path('asset/test-dep.js')

		def do_test():
			f = open(main,'w')
			f.write("//= require test-dep\n")
			f.close()

			f = open(dep,'w')
			f.write("a;")
			f.close()

			asset = self.get_asset("test-main.js")

			assert asset.is_fresh(self.env)

			f = open(dep,'w')
			f.write("b;")
			f.close()

			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(dep,(new_time,new_time))

			assert asset.is_stale(self.env)

		self.sandbox(main,dep,callback=do_test)

	def testAssetIsStaleWhenSourceFileRemoved(self):
		''' Test asset is stale when one of it's source files is removed '''

		main = self.fixture_path('asset/test-main.js')
		dep = self.fixture_path('asset/test-dep.js')

		def do_test():
			f = open(main,'w')
			f.write("//= require test-dep\n")
			f.close()

			f = open(dep,'w')
			f.write("a;")
			f.close()

			asset = self.get_asset("test-main.js")

			assert asset.is_fresh(self.env)

			os.unlink(dep)

			assert asset.is_stale(self.env)

		self.sandbox(main,dep,callback=do_test)

	def testAssetIsStaleWhenDependencyChanged(self):
		''' Test asset is stale when one of it's dependencies is modified '''

		main = self.fixture_path('asset/test-main.js')
		dep = self.fixture_path('asset/test-dep.js')

		def do_test():
			f = open(main,'w')
			f.write("//= depend_on test-dep\n")
			f.close()

			f = open(dep,'w')
			f.write("a;")
			f.close()

			asset = self.get_asset("test-main.js")

			assert asset.is_fresh(self.env)

			f = open(dep,'w')
			f.write("b;")
			f.close()

			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(dep,(new_time,new_time))

			assert asset.is_stale(self.env)

		self.sandbox(main,dep,callback=do_test)

	def testAssetIsStaleWhenDependencyRemoved(self):
		''' Test asset is stale when one of it's dependencies is removed '''

		main = self.fixture_path('asset/test-main.js')
		dep = self.fixture_path('asset/test-dep.js')

		def do_test():
			f = open(main,'w')
			f.write("//= depend_on test-dep\n")
			f.close()

			f = open(dep,'w')
			f.write("a;")
			f.close()

			asset = self.get_asset("test-main.js")

			assert asset.is_fresh(self.env)

			os.unlink(dep)

			assert asset.is_stale(self.env)

		self.sandbox(main,dep,callback=do_test)

	def testAssetIsStaleWhenAssetDependencyModified(self):
		''' Test asset is stale when one of it's asset dependencies is modified '''

		main = self.fixture_path('asset/test-main.js')
		dep = self.fixture_path('asset/test-dep.js')

		def do_test():
			f = open(main,'w')
			f.write("//= depend_on_asset test-dep\n")
			f.close()

			f = open(dep,'w')
			f.write("a;")
			f.close()

			asset = self.get_asset("test-main.js")

			assert asset.is_fresh(self.env)

			f = open(dep,'w')
			f.write("b;")
			f.close()

			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(dep,(new_time,new_time))

			assert 	asset.is_stale(self.env)

		self.sandbox(main,dep,callback=do_test)

	def testAssetIsStaleWhenSourceFileDependenciesModified(self):
		''' Test asset is stale when one of it's source files dependencies is modified '''

		a = self.fixture_path('asset/test-a.js')
		b = self.fixture_path('asset/test-b.js')
		c = self.fixture_path('asset/test-c.js')

		def do_test():
			f = open(a,'w')
			f.write("//= require test-b\n")
			f.close()

			f = open(b,'w')
			f.write("//= require test-c\n")
			f.close()

			f = open(c,'w')
			f.write("c;")
			f.close()

			asset_a = self.get_asset('test-a.js')
			asset_b = self.get_asset('test-b.js')
			asset_c = self.get_asset('test-c.js')

			assert asset_a.is_fresh(self.env)
			assert asset_b.is_fresh(self.env)
			assert asset_c.is_fresh(self.env)

			f = open(c,'w')
			f.write("x;")
			f.close()

			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(c,(new_time,new_time))

			assert asset_a.is_stale(self.env)
			assert asset_b.is_stale(self.env)
			assert asset_c.is_stale(self.env)

		self.sandbox(a,b,c,callback=do_test)

	def testAssetIsStaleWhenAssetDependencyDependenciesModified(self):
		''' Test asset is stale when one of it's asset depenency dependencies is modified '''

		a = self.fixture_path('asset/test-a.js')
		b = self.fixture_path('asset/test-b.js')
		c = self.fixture_path('asset/test-c.js')

		def do_test():
			f = open(a,'w')
			f.write("//= require test-b\n")
			f.close()

			f = open(b,'w')
			f.write("//= depend_on test-c\n")
			f.close()

			f = open(c,'w')
			f.write("c;")
			f.close()

			asset_a = self.get_asset('test-a.js')
			asset_b = self.get_asset('test-b.js')
			asset_c = self.get_asset('test-c.js')

			assert asset_a.is_fresh(self.env)
			assert asset_b.is_fresh(self.env)
			assert asset_c.is_fresh(self.env)

			f = open(c,'w')
			f.write("x;")
			f.close()

			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(c,(new_time,new_time))

			assert asset_a.is_stale(self.env)
			assert asset_b.is_stale(self.env)
			assert asset_c.is_stale(self.env)

		self.sandbox(a,b,c,callback=do_test)

	def testAssetIsStaleIfFileAddedToRequireDir(self):
		''' Test asset is stale if a file is added to its require directory '''

		asset = self.get_asset("tree/all_with_require_directory.js")
		assert asset.is_fresh(self.env)

		dirname = os.path.join(self.fixture_path("asset"),"tree/all")
		filename = os.path.join(dirname,'z.js')

		def do_test():
			f = open(filename,'w')
			f.write('z')
			f.close()

			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(filename,(new_time,new_time))

			assert asset.is_stale(self.env)

		self.sandbox(filename,callback=do_test)

	def testAssetIsStaleIfFileAddedToRequireTree(self):
		''' Test asset is stale if a file is added to its require tree '''

		asset = self.get_asset("tree/all_with_require_tree.js")
		assert asset.is_fresh(self.env)

		dirname = os.path.join(self.fixture_path("asset"),"tree/all/b/c")
		filename = os.path.join(dirname,'z.js')

		def do_test():
			f = open(filename,'w')
			f.write('z')
			f.close()

			new_time = int(time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple()))
			os.utime(filename,(new_time,new_time))

			assert asset.is_stale(self.env)

		self.sandbox(filename,callback=do_test)

	def testAssetIsStaleIfDeclaredDependencyChanges(self):
		''' Test asset is stale if it's declared dependecy is changed '''

		sprite = self.fixture_path('asset/sprite.css.mako')
		image = self.fixture_path('asset/POW.png')

		def do_test():
			asset = self.get_asset('sprite.css')

			assert asset.is_fresh(self.env)

			f = open(image,'w')
			f.write('(change)')
			f.close()

			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(image,(new_time,new_time))

			assert asset.is_stale(self.env)

		self.sandbox(sprite,image,callback=do_test)

class StaticAssetTest(RivetsTest,AssetTests):

	def setUp(self):
		self.env = rivets.Environment()
		self.env.append_path(self.fixture_path('asset'))
		self.env.cache = {}

		self.asset = self.env['POW.png']

	def testLogicalPathCanFindItself(self):
		''' Test logical path can find itself '''
		self.assertEqual(
				self.asset,
				self.env[self.asset.logical_path]
			)

	def testClass(self):
		''' Test class '''
		self.assertIsInstance(self.asset,rivets.assets.StaticAsset)

	def testContentType(self):
		''' Test content type '''
		self.assertEqual("image/png",self.asset.content_type)

	def testLength(self):
		''' Test length '''
		self.assertEqual(42917,self.asset.length)

	def testSplat(self):
		''' Test splat '''
		self.assertEqual([self.asset],self.asset.to_list())

	def testDependencies(self):
		''' Test dependencies '''
		self.assertEqual([],self.asset.dependencies)

	def testToPath(self):
		''' Test to_path '''
		self.assertEqual(self.fixture_path('asset/POW.png'),self.asset.to_path())

	def testBodyIsEntireContents(self):
		''' Test body is entire contents '''
		self.assertEqual(str(self.asset),self.asset.body)

	def testAssetIsFreshIfMtimeChangedButContentsTheSame(self):
		''' Test asset is fresh if it's mtime is changed but its 
			contents  are the same
		'''
		filename = self.fixture_path('asset/test-POW.png')

		def do_test():
			f = open(filename,'w')
			f.write("a")
			f.close()

			asset = self.env['test-POW.png']

			assert asset.is_fresh(self.env)
			f = open(filename,'w')
			f.write("a")
			f.close()

			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(filename,(new_time,new_time))

			assert asset.is_fresh(self.env)

		self.sandbox(filename,callback=do_test)

	def testAssetIsStaleWhenContentsChanged(self):
		''' Test asset is stale when it's contents have changed '''

		filename = self.fixture_path('asset/POW.png')

		def do_test():
			f = open(filename,'w')
			f.write("a")
			f.close()

			asset = self.env['POW.png']

			assert asset.is_fresh(self.env)

			f = open(filename,'w')
			f.write("b")
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(filename,(new_time,new_time))

			assert asset.is_stale(self.env)

		self.sandbox(filename,callback=do_test)

	def testAssetIsStaleIfFileRemoved(self):
		''' Test asset is stale if the file is removed '''

		filename = self.fixture_path('asset/POW.png')

		def do_test():
			f = open(filename,'w')
			f.write("a")
			f.close()

			asset = self.env['POW.png']

			assert asset.is_fresh(self.env)

			os.unlink(filename)

			assert asset.is_stale(self.env)

		self.sandbox(filename,callback=do_test)

	def testSerializingAssetToAndFromHash(self):
		''' Test serializing to and from hash '''

		expected = self.asset
		hashed = {}
		self.asset.encode_with(hashed)
		actual = rivets.assets.Asset.from_hash(self.env,hashed)

		self.assertIsInstance(actual,rivets.assets.StaticAsset)
		self.assertEqual(expected.logical_path,actual.logical_path)
		self.assertEqual(expected.pathname,actual.pathname)
		self.assertEqual(expected.content_type,actual.content_type)
		self.assertEqual(expected.length,actual.length)
		self.assertEqual(expected.digest,actual.digest)
		self.assertEqual(expected.is_fresh(self.env),actual.is_fresh(self.env))

		self.assertEqual(expected.dependencies,actual.dependencies)
		self.assertEqual(expected.to_list(),actual.to_list())
		self.assertEqual(expected.body,actual.body)
		self.assertEqual(str(expected),str(actual))

		assert actual.equals(expected) 
		assert expected.equals(actual)

class ProcessedAssetTest(RivetsTest,AssetTests,FreshnessTests):

	def setUp(self):
		self.env = rivets.Environment()
		self.env.append_path(self.fixture_path('asset'))
		self.env.cache = {}

		self.asset = self.env.find_asset('application.js',bundle=False)
		self.bundle = False

	def get_asset(self,logical_path):
		return self.env.find_asset(logical_path,bundle=self.bundle)

	def resolve(self,logical_path):
		return self.env.resolve(logical_path)

	def testLogicalPathCanFindItself(self):
		''' Test logical path can find itself '''
		self.assertEqual(
				self.asset,
				self.env.find_asset(self.asset.logical_path,bundle=False)
			)

	def testClass(self):
		''' Test class '''
		self.assertIsInstance(self.asset,rivets.assets.ProcessedAsset)

	def testContentType(self):
		''' Test content type '''
		self.assertEqual("application/javascript",self.asset.content_type)

	def testLength(self):
		''' Test length '''
		self.assertEqual(67,self.asset.length)

	def testSplat(self):
		''' Test splat '''
		self.assertEqual([self.asset],self.asset.to_list())

	def testDependencies(self):
		''' Test dependencies '''
		self.assertEqual([],self.asset.dependencies)

	def testToString(self):
		''' Test to_string '''
		self.assertEqual(
				"\ndocument.on('dom:loaded', function() {\n  $('search').focus();\n});\n",
				str(self.asset)
			)

	def testToList(self):
		''' Test to list '''
		body = ""
		for asset in self.asset.to_list():
			body += asset.body

		self.assertEqual(
				"\ndocument.on('dom:loaded', function() {\n  $('search').focus();\n});\n",
				body
			)

	def testAssetIsFreshIfItsMtimeandContentsAreTheSame(self):
		''' Test asset is fresh if it's mtime and contents are the same '''

		assert self.asset.is_fresh(self.env)

	

	def testSerializingAssetToAndFromHash(self):
		''' Test serializing to and from hash '''

		expected = self.asset
		hashed = {}
		self.asset.encode_with(hashed)
		actual = rivets.assets.Asset.from_hash(self.env,hashed)

		self.assertIsInstance(actual,rivets.assets.ProcessedAsset)
		self.assertEqual(expected.logical_path,actual.logical_path)
		self.assertEqual(expected.pathname,actual.pathname)
		self.assertEqual(expected.content_type,actual.content_type)
		self.assertEqual(expected.length,actual.length)
		self.assertEqual(expected.digest,actual.digest)
		self.assertEqual(expected.is_fresh(self.env),actual.is_fresh(self.env))

		self.assertEqual(expected.dependencies,actual.dependencies)
		self.assertEqual(expected.to_list(),actual.to_list())
		self.assertEqual(expected.body,actual.body)
		self.assertEqual(str(expected),str(actual))

		assert actual.equals(expected) 
		assert expected.equals(actual)


class BundledAssetTest(RivetsTest,AssetTests,FreshnessTests):

	def setUp(self):
		self.env = rivets.Environment()
		self.env.append_path(self.fixture_path('asset'))
		self.env.cache = {}

		self.asset = self.env['application.js']
		self.bundle = True

	def get_asset(self,logical_path):
		return self.env.find_asset(logical_path,bundle=self.bundle)

	def resolve(self,logical_path):
		return self.env.resolve(logical_path)

	def read(self,logical_path):
		return open(self.resolve(logical_path)).read()

	def testLogicalPathCanFindItself(self):
		''' Test logical path can find itself '''
		self.assertEqual(self.asset,self.env[self.asset.logical_path])

	def testClass(self):
		''' Test class '''
		self.assertIsInstance(self.asset,rivets.assets.BundledAsset)

	def testContentType(self):
		''' Test content type '''
		self.assertEqual('application/javascript',self.asset.content_type)

	def testLength(self):
		''' Test length '''
		self.assertEqual(157,self.asset.length)

	def testToString(self):
		''' Test to_string '''
		self.assertEqual(
				"var Project = {\n  find: function(id) {\n  }\n};\nvar Users = {\n  find: function(id) {\n  }\n};\n\ndocument.on('dom:loaded', function() {\n  $('search').focus();\n});\n",
				str(self.asset)
			)

	def testMTimeBasedOnRequiredAssets(self):
		''' Test mtime is based on required assets '''
		required_asset = self.fixture_path('asset/dependencies/b.js')

		def do_test():
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(required_asset,(new_time,new_time))
			self.assertEqual(int(new_time),int(self.get_asset('required_assets.js').mtime))

		self.sandbox(required_asset,callback=do_test)

	def testMTimeBasedOnDependencyPaths(self):
		''' Test mtime is based on dependency paths '''
		asset_dependency = self.fixture_path('asset/dependencies/b.js')

		def do_test():
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(asset_dependency,(new_time,new_time))
			self.assertEqual(int(new_time),int(self.get_asset('dependency_paths.js').mtime))

		self.sandbox(asset_dependency,callback=do_test)

	def testRequiringTheSameFileMultipleTimesHasNoEffect(self):
		''' Test requiring the same file multiple times has no effect '''

		self.assertEqual(
				self.read('project.js') + "\n",
				str(self.get_asset('multiple.js'))
			)

	def testRequiringAFileOfADifferentFormatRaisesAnException(self):
		''' Test requiring a file of a different format raises an exception '''
		self.assertRaises(
				rivets.errors.ContentTypeMismatch,
				self.get_asset,
				'mismatch.js'
			)

	def testSplattedAssetIncludesItself(self):
		''' Test splatted asset includes itself '''
		self.assertEqual(
				[self.resolve('project.js')],
				[asset.pathname for asset in self.get_asset('project.js').to_list()]
			)

	def testSplatterAssetsAreProcessedAssets(self):
		''' Test splatted assets are processed assets '''

		for asset in self.get_asset('project.js').to_list():
			self.assertIsInstance(asset,rivets.assets.ProcessedAsset)

	def testAssetDoesntIncludeSelfAsDependency(self):
		''' Test asset doesn't include self as dependency '''

		self.assertEqual([],self.get_asset('project.js').dependencies)

	def testAssetWithChildDependencies(self):
		''' Test asset with child dependencies '''

		self.assertEqual(
				[self.resolve('project.js'),self.resolve("users.js")],
				[a.pathname for a in self.get_asset('application.js').dependencies]
			)

	def testSplattedAssetWithChildDependencies(self):
		''' Test splatted asset with child dependencies '''

		self.assertEqual(
				[self.resolve('project.js'),self.resolve("users.js"),self.resolve('application.js')],
				[a.pathname for a in self.get_asset('application.js').to_list()]
			)

	def testBundledAssetBodyIsJustItsOwnContents(self):
		''' Test bundled asset body is just it's own contents '''

		self.assertEqual(
				"\ndocument.on('dom:loaded', function() {\n  $('search').focus();\n});\n",
				self.get_asset('application.js').body
			)

	def testBundlingJoinsFilesWithBlankLine(self):
		''' Test bundling joins files with blank line '''

		self.assertEqual(
				"var Project = {\n  find: function(id) {\n  }\n};\nvar Users = {\n  find: function(id) {\n  }\n};\n\ndocument.on('dom:loaded', function() {\n  $('search').focus();\n});\n",
				str(self.get_asset('application.js'))
			)

	def testDependenciesAppearInTheSourceBeforeFilesThatRequiredThem(self):
		''' Test dependencies appear in the source before files that required them '''

		self.assertRegexpMatches(str(self.get_asset('application.js')),re.compile(r"""Project.+Users.+focus""",re.M|re.S))

	def testProcessingASourceFileWithNoEngineExtensions(self):
		''' Test processing a source file with no engine extensions '''

		self.assertEqual(
				self.read('users.js'),
				str(self.get_asset('noengine.js'))
			)

	def testProcessingASourceFileWithOneEngineExtension(self):
		''' Test processing a source file with one engine extension '''

		self.assertEqual(
				self.read('users.js'),
				str(self.get_asset('oneengine.js'))
			)

	def testProcessingASourceFileWithMultipleEngineExtension(self):
		''' Test processing a source file with multiple engine extension '''

		self.assertEqual(
				self.read('users.js'),
				str(self.get_asset('multipleengine.js'))
			)

	def testProcessingASourceFileWithUnknownExtensions(self):
		''' Test processing a source file with unknown extensions '''
		self.assertEqual(
				self.read('users.js') + "var jQuery;\n",
				str(self.get_asset('unknownexts.min.js'))
			)

	def testIncludedDependenciesAreInsertedAfterTheHeaderOfTheDependentFile(self):
		''' Test included dependencies are inserted after the header of the dependent file '''

		self.assertEqual(
				"# My Application\n\n" + self.read("project.js") + "\n\nhello();\n",
				str(self.get_asset('included_header.js'))
			)

	def testRequiringAFileWithARelativePath(self):
		''' Test requiring a file with a relative path ''' 

		self.assertEqual(
				self.read('project.js') + "\n",
				str(self.get_asset('relative/require.js'))
			)

	def testIncludingAFileWithARelativePath(self):
		''' Test including a file with a relative path ''' 

		self.assertEqual(
				"// Included relatively\n\n" + self.read("project.js") + "\n\nhello();\n",
				str(self.get_asset('relative/include.js'))
			)

	def testCantRequireFilesOutsideTheLoadPath(self):
		''' Test can't require files outside the load path '''

		self.assertRaises(
				rivets.errors.FileOutsidePaths,
				self.get_asset,
				"relative/require_outside_path.js"
			)

	def testCantRequireAbsoluteFilesOutsideTheLoadPath(self):
		''' Test can't require absolute files outside the load path '''

		self.assertRaises(
				rivets.errors.FileOutsidePaths,
				self.get_asset,
				"absolute/require_outside_path.js"
			)

	def testRequireDirectoryRequiresAllChildFilesInAlphabeticalOrder(self):
		''' Test require_directory requires all child files in alphabetical order '''

		self.assertEqual(
				'ok(\"b.js.mako\");\n',
				str(self.get_asset('tree/all_with_require_directory.js'))
			)

	def testRequireDirectoryCurrentDirectoryIncludesSelfLast(self):
		''' Test require_directory current directory includes self last '''

		self.assertEqual(
				"var Bar;\nvar Foo;\nvar App;\n",
				str(self.get_asset("tree/directory/application.js"))
			)

	def testRequireTreeRequiresAllDescendantFilesInAlphabeticalOrder(self):
		''' Test require_tree requires all descendant files in alphabetical order '''

		self.assertEqual(
				str(self.get_asset('tree/all_with_require.js')),
				str(self.get_asset('tree/all_with_require_tree.js')),
			)

	def testRequireTreeWithoutAnArgumentDefaultsToCurrentDirectory(self):
		''' Test require_tree without an argument defaults to the current directory '''

		self.assertEqual(
				"a();\nb();\n",
				str(self.get_asset("tree/without_argument/require_tree_without_argument.js"))
			)

	def testRequireTreeWithCurrentDirectoryIncludesSelfLast(self):
		''' Test require_tree current directory includes self last '''

		self.assertEqual(
				"var Bar;\nvar Foo;\nvar App;\n",
				str(self.get_asset("tree/tree/application.js"))
			)

	def testRequireTreeWithALogicalPathArgumentRaisesAnException(self):
		''' Test require_tree with a logical path argument raises an exception '''

		self.assertRaises(
				rivets.errors.ArgumentError,
				self.get_asset,
				'tree/with_logical_path/require_tree_with_logical_path.js'
			)

	def testRequireTreeWithNonexistantPathRaisesAnException(self):
		''' Test require tree with a nonexistant path raises an exception '''

		self.assertRaises(
				rivets.errors.ArgumentError,
				self.get_asset,
				"tree/with_logical_path/require_tree_with_nonexistent_path.js"
			)

	def testRequireTreeWithNonexistantAbsolutePathRaisesAnException(self):
		''' Test require_tree with a nonexistent absolute path raises an exception ''' 

		self.assertRaises(
				rivets.errors.ArgumentError,
				self.get_asset,
				"absolute/require_nonexistent_path.js"
			)

	def testRequireTreeRespectsOrderOfChildDependencies(self):
		''' Test require tree respects order of child dependencies '''

		self.assertEqual(
				"var c;\nvar b;\nvar a;\n\n",
				str(self.get_asset('tree/require_tree_alpha.js'))
			)

	def testRequireSelfInsertsTheCurrentFilesBodyAtTheSpecifiedPoint(self):
		''' Test require_self inserts the current file's body at the specified point '''

		self.assertEqual(
				'/* b.css */\n\nb { display: none }\n/*\n\n\n\n\n\n */\n\n.one {}\n\nbody {}\n.two {}\n.project {}\n',
				str(self.get_asset("require_self.css"))
			)

	def testMultipleRequireSelfDirectivesRaisesAnError(self):
		''' Test multiple require_self directives raises an error '''

		self.assertRaises(
				rivets.errors.ArgumentError,
				self.get_asset,
				"require_self_twice.css"
			)

	def testStubSingleDependency(self):
		''' Test stub single dependency '''

		self.assertEqual(
				'var jQuery.UI = {};\n',
				str(self.get_asset('stub/skip_jquery'))
			)

	def testStubDependencyTree(self):
		''' Test stub dependency tree '''

		self.assertEqual(
				'var Foo = {};\n',
				str(self.get_asset('stub/application'))
			)

	def testCircularRequireRaisesAnError(self):
		''' Test circular require raises an error '''

		self.assertRaises(
				rivets.errors.CircularDependencyError,
				self.get_asset,
				'circle/a.js'
			)

		self.assertRaises(
				rivets.errors.CircularDependencyError,
				self.get_asset,
				'circle/b.js'
			)

		self.assertRaises(
				rivets.errors.CircularDependencyError,
				self.get_asset,
				'circle/c.js'
			)

	def testUnknownDirectivesAreIgnored(self):
		''' Test unknown directives are ignored '''

		self.assertEqual(
				"var Project = {\n  find: function(id) {\n  }\n};\n\n//\n// = Foo\n//\n// == Examples\n//\n// Foo.bar()\n// => \"baz\"\n\nvar Foo;\n",
				str(self.get_asset('documentation.js'))
			)

	def assetInheritsTheFormatExtensionAndContentTypeOfTheOriginalFile(self):
		''' Test asset inherits the format extension and content type of the original file '''

		asset = self.get_asset("project.js")
		self.assertEqual(
				"application/javascript",
				asset.content_type
			)

	if hasattr(CoffeeScriptTemplate,'default_mime_type'):
		def testAssetFallsBackToEnginesDefaultMimeType(self):
			asset = self.get_asset("default_mime_type.js")
			self.assertEqual(
					"application/javascript",
					asset.content_type
				)

	def testAssetLengthIsSourceLengthWithUnicodeCharacters(self):
		''' Test asset length is source length with unicode characters '''
		self.assertEqual(
				8,
				self.get_asset('unicode.js').length
			)

	def testAssetDigest(self):
		''' Test asset digest '''

		assert self.get_asset('project.js').digest

	def testAssetDigestPath(self):
		''' Test asset digest path '''

		assert re.match(r"""project-\w+\.js""",self.get_asset("project.js").digest_path)

	def testAssetIsFreshIfItsMtimeAndContentsAreTheSame(self):
		''' Test asset is fresh if its mtime and contents are the same '''

		assert self.get_asset('application.js').is_fresh(self.env)

	def testMultipleCharsetDefinitionsAreStrippedFromCSSBundle(self):
		''' Test multiple charset defintions are stripped from css bundle '''

		self.assertEqual(
				"@charset \"UTF-8\";\n.foo {}\n\n.bar {}\n",
				str(self.get_asset("charset.css"))
			)

	def testAppendsMissingSemicolons(self):
		''' Test appends missing semicolons '''
		
		self.assertEqual(
				"var Bar\n;\n\n(function() {\n  var Foo\n})\n;\n",
				str(self.get_asset('semicolons.js'))
			)

	def testSerializingAssetToAndFromHash(self):
		''' Test serializing to and from hash '''

		expected = self.asset
		hashed = {}
		self.asset.encode_with(hashed)
		actual = rivets.assets.Asset.from_hash(self.env,hashed)

		self.assertIsInstance(actual,rivets.assets.BundledAsset)
		self.assertEqual(expected.logical_path,actual.logical_path)
		self.assertEqual(expected.pathname,actual.pathname)
		self.assertEqual(expected.content_type,actual.content_type)
		self.assertEqual(expected.length,actual.length)
		self.assertEqual(expected.digest,actual.digest)
		self.assertEqual(expected.is_fresh(self.env),actual.is_fresh(self.env))

		self.assertEqual(expected.dependencies,actual.dependencies)
		self.assertEqual(expected.to_list(),actual.to_list())
		self.assertEqual(expected.body,actual.body)
		self.assertEqual(str(expected),str(actual))

		assert actual.equals(expected) 
		assert expected.equals(actual)

if __name__ == '__main__':
    unittest.main()