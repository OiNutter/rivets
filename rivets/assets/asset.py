from os import stat
import re

class Asset(object):
	
	def __init__(self,environment,logical_path,pathname):
		self.root = environment.root
		self.logical_path = logical_path
		self.pathname = pathname
		self.content_type = environment.get_content_type_of(pathname)
		statinfo = stat(pathname)
		self.mtime = statinfo.st_mtime
		self.size = statinfo.st_size
		self.digest = environment.get_file_digest(pathname).hexdigest()

	def digest_path(self):
		return re.sub(r"""\.(\w+)$""","%s\1"%self.digest,self.logical_path)

	def body(self):
		return self.source

	def hash(self):
		return self.digest.digest()

	def to_string(self):
		return self.source

	def equals(self,other):
		class_match = other.__class__ == self.__class__ 
		path_match = other.logical_path == self.logical_path
		time_match = other.mtime == self.mtime
		digest_match = other.digest = self.digest

		return class_match and path_match and time_match and digest_match