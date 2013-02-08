import copy

from crawl import Crawl

from base import Base
from context import Context
from index import Index
from mime import mimetype_registry
from engines import engine_registry
from processing import processor_registry
from paths import path_registry


class Environment(Base):

	def __init__(self,root="."):
		self.search_path = Crawl(root)
		self.version = ''
		self.cache = None

		self.engines = copy.deepcopy(engine_registry)
		self.mimetypes = copy.deepcopy(mimetype_registry)
		self.processors = copy.deepcopy(processor_registry)

		class ctx(Context):
			pass

		self.context_class = ctx

		for path in path_registry.paths:
			self.search_path.append_path(path)

		for extension in self.mimetypes.mimetypes.keys():
			self.search_path.append_extension(extension)

		for ext,engine in self.engines.engines.iteritems():
			self.add_engine_to_search_path(ext,engine)

	@property
	def index(self):
		return Index(self)

	def find_asset(self,path,**options):

		if not options:
			options = {}

		if not options.has_key('bundle'):
			options['bundle'] = True

		key = self.cache_key_for(path,**options)
		asset = self.assets[key] if self.assets.has_key(key) else None
		if asset and asset.is_fresh(self):
			return asset
		else:
			asset = self.index.find_asset(path,**options)
			if asset:
				return asset

		return None

	def expire_index(self):
		self._digest = None
		self.assets = {}