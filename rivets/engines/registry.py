from ..extensions import normalize_extension

class EngineRegistry:

	engines = {}

	@staticmethod
	def register_engine(extension,engine):

		ext = normalize_extension(extension)
		EngineRegistry.engines[ext] = engine

	@staticmethod
	def get_engine(extension):
		
		ext = normalize_extension(extension)

		if EngineRegistry.engines.has_key(ext):
			return EngineRegistry.engines[ext]
		else:
			return None