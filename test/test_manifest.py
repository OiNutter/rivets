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

	def setUp(self):
		self.env = rivets.Environment('.')
		self.env.append_path(self.fixture_path('default'))
		self.dir = os.path.realpath(os.path.join(tempfile.gettempdir(),'rivets/manifest'))
		self.manifest = rivets.Manifest(environment=self.env,path=os.path.join(self.dir,'manifest.json'))

	def tearDown(self):
		if os.path.exists(self.dir):
			os.rmdir(self.dir)
		assert not os.path.exists(self.dir)

	def testSpecifyFullManifestPath(self):

		directory = os.path.realpath(tempfile.gettempdir())
		path = os.path.join(directory,'manifest.json')

		manifest = rivets.Manifest(environment=self.env,path=path)

		self.assertEqual(directory,manifest.dir)
		self.assertEqual(path,manifest.path)