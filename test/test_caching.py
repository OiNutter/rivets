import sys
sys.path.insert(0,'../')
import unittest
import os
import tempfile

from rivets_test import RivetsTest
import rivets

class TestCaching(RivetsTest):

	def setUp(self):
		self.cache = {}

		self.env1 = rivets.Environment(self.fixture_path('default'))
		self.env1.append_path(".")
		self.env1.cache = self.cache

		self.env2 = rivets.Environment(self.fixture_path('symlink'))
		self.env2.append_path(".")
		self.env2.cache = self.cache

	def test_environmentDigests(self):
		''' Test environment digests are the same for different roots '''
		self.assertEqual(self.env1.get_digest().hexdigest(),self.env2.get_digest().hexdigest())

	def test_environmentCacheObjects(self):
		''' Test same environment instance cache objects are equal '''
		env = self.env1

		asset1 = env['gallery.js']
		asset2 = env['gallery.js']

		assert asset1
		assert asset2

		assert asset1 == asset2
		assert asset2 == asset1

	def test_indexCacheObjects(self):
		''' Test same index instance cache objects are equal'''
		index = self.env1.index()

		asset1 = index['gallery.js']
		asset2 = index['gallery.js']

		assert asset1
		assert asset2

		assert asset1 == asset2
		assert asset2 == asset1

	def test_environmentPathCaching(self):
		''' Test same environment instance is cached at logical and expanded path'''
		env = self.env1

		asset1 = env['gallery.js']
		asset2 = env[asset1.pathname]

		assert asset1
		assert asset2

		assert asset1 == asset2
		assert asset2 == asset1

	def test_indexPathCacing(self):
		''' Test same index instance is cached at logical and expanded path '''

		index = self.env1.index()

		asset1 = index['gallery.js']
		asset2 = index[asset1.pathname]

		assert asset1
		assert asset2

		assert asset1 == asset2
		assert asset2 == asset1

	def test_sharedCacheObjects(self):
		''' Test shared cache objects are eql '''
		asset1 = self.env1['gallery.js']
		asset2 = self.env2['gallery.js']

		assert asset1
		assert asset2

		assert asset1.equals(asset2)
		assert asset2.equals(asset1)
		assert asset1 != asset2

	def test_dependenciesAreCached(self):
		''' Test dependencies are cached '''
		env = self.env1
		
		parent = env['application.js']
		assert parent

		child1 = parent.to_list()[0]

		assert child1
		self.assertEqual('project.js',child1.logical_path)

		child2 = env.find_asset(child1.pathname,bundle=False)
		assert child2

		assert child1==child2
		assert child2==child1

	def testProcessedAndBundledAssetsCachedSeperately(self):
		''' Test processed and bundled assets are cached separately '''

		env = self.env1

		self.assertIsInstance(env.find_asset('gallery.js',bundle=False),rivets.assets.ProcessedAsset)
		self.assertIsInstance(env.find_asset('gallery.js',bundle=True),rivets.assets.BundledAsset)
		self.assertIsInstance(env.find_asset('gallery.js',bundle=False),rivets.assets.ProcessedAsset)
		self.assertIsInstance(env.find_asset('gallery.js',bundle=True),rivets.assets.BundledAsset) 

	def testProcessedAndBundledAssetsCachedSeperatelyOnIndex(self):
		''' Test processed and bundled assets are cached separately on index'''

		index = self.env1.index()

		self.assertIsInstance(index.find_asset('gallery.js',bundle=False),rivets.assets.ProcessedAsset)
		self.assertIsInstance(index.find_asset('gallery.js',bundle=True),rivets.assets.BundledAsset)
		self.assertIsInstance(index.find_asset('gallery.js',bundle=False),rivets.assets.ProcessedAsset)
		self.assertIsInstance(index.find_asset('gallery.js',bundle=True),rivets.assets.BundledAsset) 

	def testKeysConsistentIfEnvironmentDigestChanges(self):
		'''' Test keys are consistent even if environment digest changes '''

		self.env1['gallery.js']
		old_keys = self.cache.keys().sort()

		self.cache.clear()
		self.env2.version = '2.0'

		self.env2['gallery.js']
		new_keys = self.cache.keys().sort()

		self.assertEqual(old_keys,new_keys)

	def staleCachedAssetIsntLoadedIfFileRemoved(self):
		''' Test stale cached asset isn't loaded if file is removed ''' 

		filename = self.fixture_path('default/tmp.js')

		def run_test():
			f = open(filename,'w')
			f.write('foo')
			f.close()

			self.assertEqual("foo;\n",str(self.env1['tmp.js']))

			os.unlink(filename)

			self.assertIsNone(self.env2['tmp.js'])

		self.sandbox(filename,callback=run_test)

	def testStaleCachedAssetIsntLoadedIfDependencyIsChanged(self):
		''' Test stale cached asset isn't loaded if depedency is changed and removed '''

		foo = self.fixture_path("default/foo-tmp.js")
		bar = self.fixture_path("default/bar-tmp.js")

		def run_test():
			f = open(foo,'w')
			f.write('//=require bar-tmp\nfoo;')
			f.close()

			f2 = open(bar,'w')
			f2.write('bar;')
			f2.close()

			self.assertEqual("bar;\nfoo;\n",str(self.env1['foo-tmp.js']))
			self.assertEqual("bar;\n",str(self.env1["bar-tmp.js"]))

			f = open(foo,'w')
			f.write('foo;')
			f.close()

			os.unlink(bar)
			self.assertEqual("foo;\n",str(self.env1['foo-tmp.js']))
			self.assertIsNone(self.env2['bar-tmp.js'])

		self.sandbox(foo,bar,callback=run_test)

	def testStaleCachedAssetIsntLoadedIfRemovedFromPath(self):
		''' Test stale cached asset isn't loaded if removed from path '''

		env1 = rivets.Environment(self.fixture_path('default'))
		env1.append_path("app")
		env1.append_path("vendor")
		env1.cache = self.cache

		env2 = rivets.Environment(self.fixture_path('default'))
		env2.append_path("app")
		env2.cache = self.cache

		self.assertEqual("jQuery;\n",str(env1["main.js"]))
		self.assertEqual("jQuery;\n",str(env1["jquery.js"]))
		assert env1["main.js"].is_fresh(env1)

		self.assertRaises(rivets.errors.FileNotFound,lambda : str(env2["main.js"]))

class TestFileStore(RivetsTest):

	def setUp(self):
		self.cache = rivets.caching.FileStore(tempfile.gettempdir())

		self.env1 = rivets.Environment(self.fixture_path('default'))
		self.env1.append_path('.')
		self.env1.cache = self.cache

		self.env2 = rivets.Environment(self.fixture_path("symlink"))
		self.env2.append_path(".")
		self.env2.cache = self.cache

	def testSharedCacheObjectsAreEql(self):
		''' Test shared cache objects are eql '''
		asset1 = self.env1['gallery.js']
		asset2 = self.env2['gallery.js']

		assert asset1
		assert asset2

		assert asset1.equals(asset2)
		assert asset2.equals(asset1)
		assert asset1 != asset2

		
if __name__ == '__main__':
    unittest.main()