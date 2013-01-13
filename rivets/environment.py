import os
import io

from crawl import Crawl

from context import Context
from mimetypes import MimeTypeRegistry
from engines import EngineRegistry
from processing import ProcessorRegistry
from assets import AssetAttributes,BundledAsset,ProcessedAsset,StaticAsset

class Environment:

	files = []
	default_encoding = 'utf8'
	root = ""

	output_extensions = {
		".coffee":".js",
		".scss":".css"
	}
	
	def __init__(self,root="."):
		self.root = root
		self.search_path = Crawl(root)
		self.version = ''

		self.engines = EngineRegistry
		self.mimetypes = MimeTypeRegistry
		self.processors = ProcessorRegistry

		self.context_class = Context

		for extension in self.mimetypes.mimetypes.keys():
			self.search_path.append_extension(extension)

		for ext,engine in self.engines.engines.iteritems():
			self.add_engine_to_search_path(ext,engine)

	def get_digest(self):

		from version import VERSION
		from hashlib import md5
		self.digest = md5()
		self.digest.update(str(VERSION))
		self.digest.update(str(self.version))

		return self.digest.copy()

	def get_file_digest(self,path):
		if os.path.isfile(path):
			digest = self.get_digest()
			data = io.open(path,encoding = self.default_encoding).read()
			data = data.replace('\t',' ')
			digest.update(data.encode('utf8'))
			return digest
		elif os.path.isdir(path):
			entries = self.search_path.entries(path)
			return self.get_digest().update(','.join(entries).encode('utf8'))

	def paths(self):
		return self.search_path.paths

	def add_path(self,path):
		self.search_path.append_path(path)

	def add_paths(self,*paths):
		if isinstance(paths[0],list):
			paths = paths[0]

		for path in paths:
			self.search_path.append_path(path)

	def register_mimetype(self,extension,mimetype):
		self.mimetypes.register_mimetype(extension,mimetype)
		self.search_path.append_extension(extension)

	def register_engine(self,extension,engine):
		self.engines.register_engine(extension,engine)
		self.add_engine_to_search_path(extension,engine)

	def register_preprocesser(self,mimetype,processor):
		self.processors.register_preprocesser(mimetype,processor)

	def register_postprocesser(self,mimetype,processor):
		self.processors.register_postprocesser(mimetype,processor)

	def set_js_compressor(self,compressor):
		self.processors.set_js_compressor(compressor)

	def set_css_compressor(self,compressor):
		self.processors.set_css_compressor(compressor)

	def add_engine_to_search_path(self,extension,engine):
		self.search_path.append_extension(extension)

		if getattr(engine,'default_mime_type',None):
			format_ext = self.mimetypes.get_extension_for_mimetype(engine.default_mime_type)
			if format_ext:
				self.search_path.alias_extension(extension, format_ext)

	def get_attributes_for(self,path):
		return AssetAttributes(self,path)

	def get_content_type_of(self,path):
		return self.get_attributes_for(path).get_content_type()

	def find_asset(self,path,options=None):
		asset = self.search_path.find(path)

		if asset:
			return self.build_asset(asset,path,options)
		else:
			raise IOError("Couldn't find file %s in dir %s" % (path, self.root))

	def build_asset(self,logical_path,path,options=None):

		if not options:
			options = {
				"bundle":True
			}

		if self.get_attributes_for(path).get_processors():

			if not options['bundle']:
				if path not in self.files:
					return ProcessedAsset(self,logical_path,path)
			else:
				return BundledAsset(self,logical_path,path)
		else:
			return StaticAsset()

	def resolve(self,logical_path,options=None,callback=None):

		if callback:
			args = self.get_attributes_for(logical_path).search_paths() + [options]
			path = self.search_path.find(*args)
			return callback(path)
		else:
			return self.resolve(logical_path,options,lambda x: x)
		raise IOError("Couldn't find file %s" % logical_path)

	def compile(self,path):
		
		asset = self.find_asset(path)
		return asset.to_string()
