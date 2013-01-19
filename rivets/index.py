from base import Base

class Index(Base):

	def __init__(self,environment):
		self.environment = environment

		self.default_encoding = environment.default_encoding

		self.context_class = environment.context_class
		self.cache = environment.cache
		self.search_path = environment.search_path.index()
		self.digest = environment.digest
		self.version = environment.version
		self.mimetypes = environment.mimetypes
		self.engines = environment.engines
		self.processors = environment.processors

		self.assets = {}
		self.digests = {}

	def index(self):
		return self

	def get_file_digest(self,path):
		
		if not self.digests.has_key(path):
			
			self.digests[path] = super(Index,self).get_file_digest(path)

		return self.digests[path]

	def find_asset(self,path,**options):

		if not options.has_key('bundle'):
			options['bundle'] = True

		key = self.cache_key_for(path,**options)
		asset = self.assets[key] if self.assets.has_key(key) else None

		if asset:
			return asset
		else:

			asset = super(Index,self).find_asset(path,**options)

			if asset:

				logical_path_cache_key = self.cache_key_for(path,**options)
				full_path_cache_key = self.cache_key_for(asset.pathname,**options)

				self.assets[logical_path_cache_key] = self.assets[full_path_cache_key] = asset

				self.environment.assets[logical_path_cache_key] = self.environment.assets[full_path_cache_key] = asset

			return asset

	def expire_index(self):
		raise TypeError("Can't modify immutable index")

	def build_asset(self,logical_path,pathname,**options):

		key = self.cache_key_for(pathname,**options)

		if not self.assets.has_key(key):
			def get_asset():
				return super(Index,self).build_asset(logical_path,pathname,**options)

			asset = self.cache_asset(key,callback=get_asset)

			if asset:
				self.assets[key] = asset
			else:
				return None

		return self.assets[key]

