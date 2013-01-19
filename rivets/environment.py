from crawl import Crawl

from base import Base
from context import Context
from index import Index
from mimetypes import MimeTypeRegistry
from engines import EngineRegistry
from processing import ProcessorRegistry


class Environment(Base):

	def __init__(self,root="."):
		self.root = root
		self.search_path = Crawl(root)
		self.version = ''
		self.cache = None

		self.engines = EngineRegistry
		self.mimetypes = MimeTypeRegistry
		self.processors = ProcessorRegistry

		self.context_class = Context

		for extension in self.mimetypes.mimetypes.keys():
			self.search_path.append_extension(extension)

		for ext,engine in self.engines.engines.iteritems():
			self.add_engine_to_search_path(ext,engine)

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
			asset = self.index().find_asset(path,**options)
			if asset:
				return asset

		return None

	def expire_index(self):
		self.digest = None
		self.assets = {}