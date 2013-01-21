import sys
sys.path.insert(0,'../')
import unittest
import os
import inspect
from warnings import warn

from rivets_test import RivetsTest
import rivets

original_stat = os.stat
file_stat_calls = None

def new_stat(filename):
	if file_stat_calls:
		if not file_stat_calls.has_key(filename):
			file_stat_calls[filename] = 0

		file_stat_calls[filename] += 1

		if file_stat_calls[filename]>1:
			warn('Multiple os.stat(%s) calls'%filename)
			warn('\n'.join(inspect.stack()))

	return original_stat(filename)

dir_entries_calls = None
original_listdir = os.listdir

def new_listdir(dirname):
	if dir_entries_calls:
		if not dir_entries_calls.has_key(dirname):
			dir_entries_calls[dirname] = 0

		dir_entries_calls[dirname] += 1

		if dir_entries_calls[dirname]>1:
			warn('Multiple os.listdir(%s) calls'%dirname)
			warn('\n'.join(inspect.stack()))

	return original_listdir(dirname)

os.stat = new_stat
os.listdir = new_listdir

class TestPerformance(RivetsTest):

	def setUp(self):
		self.env = self.new_environment()
		self.reset_stats()

	def tearDown(self):
		global file_stat_calls, dir_entries_calls

		file_stat_calls = None
		dir_entries_calls = None

	def new_environment(self):
		env = rivets.Environment()
		env.append_path(self.fixture_path('default'))
		return env

	def reset_stats(self):
		global file_stat_calls, dir_entries_calls

		file_stat_calls = {}
		dir_entries_calls = {}

	def assertNoStatCalls(self):
		global file_stat_calls
		for path,count in file_stat_calls.iteritems():
			self.assertEqual(0,count,"os.stat('%s') called %d times"%(path,count))

		for path,count in dir_entries_calls.iteritems():
			self.assertEqual(0,count,"os.listdir('%s') called %d times"%(path,count))		

	def assertNoRedundantStatCalls(self):
		global file_stat_calls
		for path,count in file_stat_calls.iteritems():
			self.assertEqual(1,count,"os.stat('%s') called %d times"%(path,count))

		for path,count in dir_entries_calls.iteritems():
			self.assertEqual(1,count,"os.listdir('%s') called %d times"%(path,count))		

	def testSimpleFile(self):
		''' Test simple file '''
		str(self.env['gallery.js'])
		self.assertNoRedundantStatCalls()

	def testIndexedSimpleFile(self):
		''' Test indexed simple file '''
		str(self.env.index()['gallery.js'])
		self.assertNoRedundantStatCalls()

	def testFileWithDeps(self):
		''' Test file with deps '''
		str(self.env['mobile.js'])
		self.assertNoRedundantStatCalls()

	def testIndexedFileWithDeps(self):
		''' Test indexed file with deps '''
		str(self.env.index()['mobile.js'])
		self.assertNoRedundantStatCalls()

	def testCheckingFreshness(self):
		''' Test checking freshness '''
		asset = self.env['mobile.js']
		self.reset_stats()

		assert asset.is_fresh(self.env)
		self.assertNoRedundantStatCalls()

	def testCheckingFreshnessFromIndex(self):
		''' Test checking freshness from index '''
		index = self.env.index()
		asset = index["mobile.js"]
		self.reset_stats()

		assert asset.is_fresh(index)
		self.assertNoStatCalls()

	def testLoadingFromCache(self):
		''' Test loading from cache '''
		env1 = self.new_environment()
		env2 = self.new_environment()
		env1.cache = {}
		env2.cache = {}

		env1["mobile.js"]
		self.reset_stats()

		env2["mobile.js"]
		self.assertNoRedundantStatCalls()

	def testLoadingFromIndexedCache(self):
		''' Test loading from indexed cache '''

		env1 = self.new_environment()
		env2 = self.new_environment()
		env1.cache = {}
		env2.cache = {}

		env1.index()["mobile.js"]
		self.reset_stats()

		env2.index()["mobile.js"]
		self.assertNoRedundantStatCalls()

if __name__ == '__main__':
    unittest.main()