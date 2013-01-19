from asset import Asset

class StaticAsset(Asset):
	
	@property
	def source(self):
		return open(self.pathname,'r+').read()

	def to_path(self):
		return self.pathname