import os
import re
from ..errors import UnserializeError

class Asset(object):

	@staticmethod
	def from_hash(environment,asset_hash):

		if not isinstance(asset_hash,dict):
			return None

	
		try:
			klass = None
			if asset_hash['class'] == 'BundledAsset' or asset_hash['class'] == 'bundled_asset.BundledAsset':
				from bundled_asset import BundledAsset
				klass = BundledAsset
			elif asset_hash['class'] == 'ProcessedAsset' or asset_hash['class'] == 'processed_asset.ProcessedAsset':
				from processed_asset import ProcessedAsset
				klass = ProcessedAsset
			elif asset_hash['class'] == 'StaticAsset' or asset_hash['class'] == 'static_asset.StaticAsset':
				from static_asset import StaticAsset
				klass = StaticAsset

			if klass:
				asset = klass(None,None,None,init=False)
				asset.init_with(environment,asset_hash)
				return asset
		except UnserializeError:
			return None

		return None
	
	def __init__(self,environment,logical_path,pathname,init=True):
		if init:
			self.root = environment.get_root()
			self.logical_path = logical_path
			self.pathname = pathname
			self.content_type = environment.get_content_type_of(pathname)
			statinfo = environment.stat(pathname)
			self.mtime = statinfo.st_mtime
			self.size = statinfo.st_size
			self.digest = environment.get_file_digest(pathname).hexdigest()
			self.relative_pathname = None

	def init_with(self,environment,coder):
		self.root = environment.get_root()
		self.logical_path = coder['logical_path']
		self.content_type = coder['content_type']
		self.digest = coder['digest']
		self.pathname = self.expand_root_path(coder['pathname']) if coder.has_key('pathname') else ''
		self.mtime = coder['mtime']
		self.length = int(coder['length'])

	def digest_path(self):
		return re.sub(r"""\.(\w+)$""","%s\1"%self.digest,self.logical_path)

	def body(self):
		return self.source

	def hash(self):
		return self.digest.digest()

	def to_string(self):
		return self.source

	def __str__(self):
		return self.to_string()

	def __iter__(self):
		return self.to_list()

	def to_list(self):
		return [self]

	def equals(self,other):
		class_match = other.__class__ == self.__class__ 
		path_match = os.path.realpath(other.logical_path) == os.path.realpath(self.logical_path)
		time_match = other.mtime == self.mtime
		digest_match = other.digest == self.digest

		return class_match and path_match and time_match and digest_match

	def encode_with(self,coder):
		coder['class'] = re.sub(r"""rivets.assets.""",'',self.__class__.__name__)
		coder['logical_path'] = self.logical_path
		coder['pathname'] = self.relativize_root_path(self.pathname)
		coder['content_type'] = self.content_type
		coder['mtime']=self.mtime
		coder['length'] = self.length
		coder['digest'] = self.digest
		return coder

	def is_fresh(self,environment):
		return self.is_dependency_fresh(environment,self)

	def is_stale(self,environment):
		return not self.is_fresh(environment)

	def relative_pathname(self):
		return self.relative_pathname if self.relative_pathname else self.relativize_root_path(self.pathname)

	def expand_root_path(self,path):
		return re.sub(r"""^\$root""",self.root,path)

	def relativize_root_path(self,path):
		return re.sub(r"""^%s"""%re.escape(self.root),'$root',path)

	def is_dependency_fresh(self,environment,dep):
		path,mtime,hexdigest = dep.pathname, dep.mtime,dep.digest

		stat = environment.stat(path)

		if not stat:
			return False

		if mtime >= stat.st_mtime:
			return True

		digest = environment.get_file_digest(self.pathname)

		if hexdigest == digest.hexdigest():
			return True

		return False
