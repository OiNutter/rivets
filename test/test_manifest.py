import sys
sys.path.insert(0,'../')
if sys.version_info[:2] == (2,6):
	import unittest2 as unittest
else:
	import unittest
import os
import tempfile

from rivets_test import RivetsTest
import rivets

class TestManifest(RivetsTest):

	def setup(self):
		self.env = rivets.Environment('.')
		self.env.append_path(self.fixture_path('default'))
		self.dir = os.path.join(tempfile.tempdir,'rivets/manifest')
		self.manifest = rivets.Manifest(environment=self.env,path=os.path.join(self.dir,'manifest.json'))

	def teardown(self):
		os.rmdir(self.dir)
		assert not os.listdir("%s/*"%self.dir)

	def testSpecifyFullManifestPath(self):

		directory = tempfile.tempdir
		path = os.path.join(directory,'manifest.json')

		manifest = rivets.Manifest(environment=self.env,path=path)

		self.assertEqual(directory,manifest.dir)
		self.assertEqual(path,manifest.path)