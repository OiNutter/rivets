from asset import Asset
from os import stat
import regex as re

from ..errors import UnserializeError
from ..utils import unique_list

class ProcessedAsset(Asset):
	
	def __init__(self,environment,logical_path,pathname,init=True):
		if init:
			super(ProcessedAsset,self).__init__(environment,logical_path,pathname)

			context = environment.context_class(environment,logical_path,pathname)

			self.source = context.evaluate(pathname)
			self.length = len(self.source)
			digest = environment.digest
			digest.update(self.source.encode('utf8'))
			self.digest = digest.hexdigest()

			self.build_required_assets(environment,context)
			self.build_dependency_paths(environment,context)

			self.dependency_digest = self.compute_dependency_digest(environment)

	def init_with(self,environment,coder):
		super(ProcessedAsset,self).init_with(environment,coder)

		self.source = coder['source']
		self.dependency_digest = coder['dependency_digest']
		self.required_assets = []

		for path in coder['required_paths']:
			p = self.expand_root_path(path)

			matched = False
			for search_path in environment.search_path.paths:
				if re.search(re.escape(search_path),p):
					matched = True

			if not matched:
				raise UnserializeError("%s isn't in paths" % p)

			self.required_assets.append(self if p == self.pathname else environment.find_asset(p,bundle = False))

		self.dependency_paths = []

		for dep in coder['dependency_paths']:
			self.dependency_paths.append(DependencyFile(self.expand_root_path(dep['path']),dep['mtime'],dep['digest']))

	def encode_with(self,coder):
		coder = super(ProcessedAsset,self).encode_with(coder)

		coder['source'] = self.source
		coder['dependency_digest'] = self.dependency_digest

		coder['required_paths'] = []

		for asset in self.required_assets:
			coder['required_paths'].append(self.relativize_root_path(asset.pathname))

		coder['dependency_paths'] = []

		for dep in self.dependency_paths:
			coder['dependency_paths'].append({
					'path':self.relativize_root_path(dep.pathname),
					'mtime':dep.mtime,
					'digest':dep.digest

				})

		return coder

	def is_fresh(self,environment):
		fresh = True

		for dep in self.dependency_paths:
			fresh = self.is_dependency_fresh(environment,dep)

			if not fresh:
				break

		return fresh

	def build_required_assets(self,environment,context):
		include_paths = context.required_paths
		include_paths.append(self.pathname)
		to_include = unique_list(self.resolve_dependencies(environment,include_paths))
		stubbed = unique_list(self.resolve_dependencies(environment,unique_list(context.stubbed_assets)))

		self.required_assets = [x for x in to_include if x not in stubbed]

	def resolve_dependencies(self,environment,paths):
		assets = []
		cache = {}

		for path in paths:
			if path == self.pathname:
				if not cache.has_key(self) or not cache[self]:
					cache[self] = True
					assets.append(self)
			else:
				asset = environment.find_asset(path, bundle=False)
				if asset:
					for asset_dependency in asset.required_assets:
						if not cache.has_key(asset_dependency) or not cache[asset_dependency]:
							cache[asset_dependency] = True
							assets.append(asset_dependency)

		return assets

	def build_dependency_paths(self,environment,context):
		dependency_paths = {}

		for path in context.dependency_paths:
			digest = environment.get_file_digest(path)
			dep = DependencyFile(path, stat(path).st_mtime, digest.hexdigest())
			dependency_paths[dep] = True

		for path in unique_list(context.dependency_assets):
			if path == str(self.pathname):
				digest = environment.get_file_digest(path)
				dep = DependencyFile(self.pathname, stat(path).st_mtime, digest.hexdigest())
				dependency_paths[dep] = True
			else:
				asset = environment.find_asset(path,bundle= False)
				if asset:
					for dep in asset.dependency_paths:
						dependency_paths[dep] = True

		self.dependency_paths = dependency_paths.keys()

	def compute_dependency_digest(self,environment):

		digest = environment.digest
		for asset in self.required_assets:
			digest.update(asset.digest)

		return digest.hexdigest()

class DependencyFile:

	def __init__(self,pathname, mtime, digest):
          self.pathname = pathname
          self.mtime    = int(mtime)
          self.digest = digest

	def equals(self,other):
		return isinstance(other,DependencyFile) and self.pathname == other.pathname and self.mtime == other.mtime and self.digest == other.digest

	def hash(self,other):
		from hashlib import md5
		return md5().update(self.pathname)
        