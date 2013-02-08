from ..extensions import normalize_extension

class EngineRegistry(object):

	def __init__(self):
		self.engines = {}

	def register_engine(self,extension,engine):

		ext = normalize_extension(extension)

		self.engines[ext] = engine

	def get_engine(self,extension):
		
		ext = normalize_extension(extension)

		if self.engines.has_key(ext):
			return self.engines[ext]
		else:
			return None

	def __getitem__(self,extension):
		return self.get_engine(extension)

	@property
	def engine_extensions(self):

		return self.engines.keys()