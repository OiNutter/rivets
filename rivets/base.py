import os
import io
from hashlib import md5
import json

from assets import Asset, AssetAttributes, BundledAsset, ProcessedAsset, StaticAsset
from errors import FileNotFound


class Base(object):

	default_encoding = 'utf8'
	digest = None

	def get_digest(self):

		if not self.digest:
			from version import VERSION
			self.digest = md5()
			self.digest.update(str(VERSION))
			self.digest.update(str(self.version))

		return self.digest.copy()

	def get_file_digest(self,path):
		if os.path.isfile(path):
			digest = self.get_digest()
			data = open(path).read()
			data = data.replace('\t',' ')
			digest.update(data)
			return digest
		elif os.path.isdir(path):
			entries = self.search_path.entries(path)
			return self.get_digest().update(','.join(entries).encode('utf8'))

	def get_root(self):
		return self.search_path.root

	def paths(self):
		return self.search_path.paths

	def prepend_path(self,*paths):
		self.prepend_paths(*paths)

	def prepend_paths(self,*paths):
		self.expire_index()
		self.search_paths.append_paths(*paths)

	def append_path(self,*paths):
		self.append_paths(*paths)

	def append_paths(self,*paths):
		self.expire_index()
		self.search_path.append_paths(*paths)

	def clear_paths(self):
		self.expire_index()
		for path in self.search_path.paths:
			self.search_path.paths.remove_path(path)

	def register_mimetype(self,extension,mimetype):
		self.expire_index()
		self.mimetypes.register_mimetype(extension,mimetype)
		self.search_path.append_extension(extension)

	def register_engine(self,extension,engine):
		self.expire_index()
		self.engines.register_engine(extension,engine)
		self.add_engine_to_search_path(extension,engine)

	def register_preprocessor(self,mimetype,processor,callback=None):
		self.expire_index()
		self.processors.register_preprocessor(mimetype,processor,callback)

	def unregister_preprocessor(self,mimetype,processor):
		self.expire_index()
		self.processors.unregister_preprocessor(mimetype,processor)

	def register_postprocessor(self,mimetype,processor,callback=None):
		self.expire_index()
		self.processors.register_postprocessor(mimetype,processor,callback)

	def unregister_postprocessor(self,mimetype,processor):
		self.expire_index()
		self.processors.unregister_postprocessor(mimetype,processor)

	def register_bundleprocessor(self,mimetype,processor,callback=None):
		self.expire_index()
		self.processors.register_bundleprocessor(mimetype,processor,callback)

	def unregister_bundleprocessor(self,mimetype,processor):
		self.expire_index()
		self.processors.unregister_bundleprocessor(mimetype,processor)

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

	def index(self):
		raise NotImplementedError('Index Not Implemented in Base class')

	def entries(self,path):
		return self.search_path.entries(path)

	def stat(self,path):
		return self.search_path.stat(path)

	def get_attributes_for(self,path):
		return AssetAttributes(self,path)

	def get_content_type_of(self,path):
		return self.get_attributes_for(path).get_content_type()

	def __getitem__(self,path):
		return self.find_asset(path)

	def find_asset(self,path,**options):
		logical_path = path

		if os.path.isabs(path):
			if not self.stat(path):
				return None
			logical_path = self.get_attributes_for(path).get_logical_path()
		else:
			try:
				path = self.resolve(logical_path)

				filename,extname = os.path.splitext(path)

				if extname == "":
					expanded_logical_path = self.get_attributes_for(path).get_logical_path()
					newfile,newext = os.path.splitext(expanded_logical_path)
					logical_path += newext
			except FileNotFound:
				return None

		return self.build_asset(logical_path,path,**options)

	def build_asset(self,logical_path,path,**options):

		if not options.has_key('bundle'):
			options["bundle"] = True

		if self.get_attributes_for(path).get_processors():

			if not options['bundle']:
				return ProcessedAsset(self,logical_path,path)
			else:
				return BundledAsset(self,logical_path,path)
		else:
			return StaticAsset()

	def resolve(self,logical_path,**options):

		if options.has_key('callback') and options['callback']:
			callback = options.pop('callback')
			def process_asset(path):
				if path:
					if os.path.basename(path)=='component.json':
						component = json.loads(open(path).read())

						if component.has_key('main'):
							if isinstance(component['main'],str):
								return options['callback'](os.path.join(os.path.dirname(path),component['main']))
							elif isinstance(component['main'],list):
								filename,ext = os.path.splitext(logical_path)

								for fn in component['main']:
									fn_name,fn_ext = os.path.splitext(fn)
									if ext == "" or ext == fn_ext:
										return callback(os.path.join(os.path.dirname(path),fn))

					else:
						return callback(path)

			args = self.get_attributes_for(logical_path).search_paths()
			path = self.search_path.find(*args,**options)
			asset = process_asset(path)
		else:
			options['callback'] = lambda x: x
			asset = self.resolve(logical_path,**options)
		if asset:
			return asset
		raise FileNotFound("Couldn't find file %s" % logical_path)

	def compile(self,path):
		
		asset = self.find_asset(path)
		return asset.to_string()

	###########
	# Caching #
	###########

	def cache_key_for(self,path,**options):
		return "%s:%i" % (path,1 if options.has_key('bundle') and options['bundle'] else 0)

	def cache_get(self,key):

		if hasattr(self.cache,'get'):
			return self.cache.get(key)

		return None

	def cache_set(self,key,value):

		if hasattr(self.cache,'set'):
			return self.cache.set(key,value)

	def cache_asset(self,path,callback=None):

		if self.cache is None:
			return callback()
		else:
			asset = Asset.from_hash(self,self.cache_get_hash(path))
			if asset and asset.is_fresh(self):
				return asset
			elif callback:
				asset = callback()

				if asset:
					asset_hash = {}
					asset_hash = asset.encode_with(asset_hash)

					self.cache_set_hash(path,asset_hash)

					if path != asset.pathname:
						self.cache_set_hash(asset.pathname,asset_hash)

					return asset

		return None

	def expand_cache_key(self,key):
		h = md5()
		h.update(key.replace(self.get_root(),''))
		return os.path.join('rivets',h.hexdigest())

	def cache_get_hash(self,key):
		asset_hash = self.cache_get(self.expand_cache_key(key))
		if asset_hash and isinstance(asset_hash,dict) and self.get_digest().hexdigest() == asset_hash['_version']:
			return asset_hash

		return None

	def cache_set_hash(self,key,asset_hash):
		asset_hash['_version'] = self.get_digest().hexdigest()
		self.cache_set(self.expand_cache_key(key),asset_hash)
		return asset_hash