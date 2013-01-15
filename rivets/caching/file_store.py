import os
import pickle

class FileStore:

	def __init__(self,root):
		self.root = os.path.abspath(root)

	def get(self,key):
		pathname = os.path.join(self.root,key)
		return pickle.load(open(pathname,'rb')) if os.path.exists(pathname) else None

	def set(self,key,value):
		path = os.path.join(self.root,key)
		dirname = os.path.dirname(path)

		if not os.path.exists(dirname):
			os.makedirs(dirname)

		f = open(path,'w')
		pickle.dump(value,f)
		return value