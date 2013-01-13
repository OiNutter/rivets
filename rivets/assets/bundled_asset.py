from asset import Asset
from ..utils import unique_list

class BundledAsset(Asset):

	def __init__(self,environment,logical_path,pathname):
		super(BundledAsset,self).__init__(environment,logical_path,pathname)

		self.processed_asset = environment.find_asset(pathname,{'bundle':False})
		self.required_assets = self.processed_asset.required_assets
		self.dependency_paths = unique_list(self.processed_asset.dependency_paths)

		self.source = ""

		for dependency in self.to_list():
			self.source += dependency.to_string()

		context = environment.context_class(environment,logical_path,pathname)
		self.source = context.evaluate(pathname,{'data':self.source,'processors':environment.processors.get_bundleprocessors(self.content_type)})

		self.mtime = max(set(self.to_list()) | set(self.dependency_paths),key=lambda x:x.mtime)
		self.length = len(self.source)
		digest = environment.get_digest()
		digest.update(self.source.encode('utf8'))
		self.digest = digest.hexdigest()

	def body(self):
		return self.processed_asset.source

	def get_dependencies(self):
		return [a for a in self.to_list() if not a.equals(self.processed_asset)]

	def to_list(self):
		return self.required_assets