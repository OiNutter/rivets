from asset import Asset
from ..utils import unique_list
from ..errors import UnserializeError

class BundledAsset(Asset):

	def __init__(self,environment,logical_path,pathname,init=True):
		if init:
			super(BundledAsset,self).__init__(environment,logical_path,pathname)

			self.processed_asset = environment.find_asset(pathname,bundle=False)
			self.required_assets = self.processed_asset.required_assets if self.processed_asset else []
			self.dependency_paths = unique_list(self.processed_asset.dependency_paths) if self.processed_asset else []

			self.source = ""

			for dependency in self.to_list():
				self.source += dependency.to_string()

			context = environment.context_class(environment,logical_path,pathname)
			self.source = context.evaluate(pathname,data=self.source, processors=environment.processors.get_bundleprocessors(self.content_type))

			self.mtime = max(set(self.to_list()) | set(self.dependency_paths),key=lambda x:x.mtime).mtime
			self.length = len(self.source)
			digest = environment.digest
			digest.update(self.source.encode('utf8'))
			self.digest = digest.hexdigest()

	def init_with(self,environment,coder):
		super(BundledAsset,self).init_with(environment,coder)

		self.processed_asset = environment.find_asset(self.pathname,bundle=False)
		self.required_assets = self.processed_asset.required_assets

		if self.processed_asset.dependency_digest != coder['required_assets_digest']:
			raise UnserializeError('processed asset belongs to a stale environment')

		self.source = coder['source']

	def encode_with(self,coder):
		coder = super(BundledAsset,self).encode_with(coder)

		coder['source'] = self.source
		coder['required_assets_digest'] = self.processed_asset.dependency_digest

		return coder

	def body(self):
		return self.processed_asset.source

	def get_dependencies(self):
		return [a for a in self.to_list() if not a.equals(self.processed_asset)]

	def to_list(self):
		return self.required_assets

	def is_fresh(self,environment):
		return self.processed_asset.is_fresh(environment)