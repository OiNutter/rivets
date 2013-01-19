import os
import unittest
import shutil

class RivetsTest(unittest.TestCase):

	FIXTURE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),'fixtures'))

	def fixture(self,path):
		return open(path).read()

	def fixture_path(self,path):
		if path == self.FIXTURE_ROOT:
			return path
		else:
			return os.path.join(self.FIXTURE_ROOT,path)

	def sandbox(self,*paths,**kwargs):
		backup_paths = []
		remove_paths = []

		callback = kwargs.pop('callback',None)

		for path in paths:
			if os.path.exists(path):
				backup_paths.append(path)
			else:
				remove_paths.append(path)

			return callback()
		try:
			for path in backup_paths:
				shutil.copytree(path,"%s.orig"%path)

		finally:
			for path in backup_paths:
				if os.path.exists(path):
					shutil.move("%s.orig"%path,path)

				assert not os.path.exists("%s.orig"%path)

			for path in remove_paths:
				if os.path.exists(path):
					shutil.rmtree(path)

				assert not os.path.exists(path)

	def assertIsNone(self,val):
		if hasattr(super(RivetsTest,self),'assertIsNone'):
			super(RivetsTest,self).assertIsNone(val)
		else:
			self.assertEqual(None,val)


	def assertIsInstance(self,val,klass):
		if hasattr(super(RivetsTest,self),'assertIsInstance'):
			super(RivetsTest,self).assertIsInstance(val,klass)
		else:
			assert isinstance(val,klass)