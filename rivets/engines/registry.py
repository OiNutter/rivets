from ..extensions import normalize_extension
from ..utils import unique_list

class EngineRegistry:

	engines = {}

	@staticmethod
	def register_engine(extension,engine):

		ext = normalize_extension(extension)

		if not EngineRegistry.engines.has_key(ext):
			EngineRegistry.engines[ext] = []	
		
		EngineRegistry.engines[ext].append(engine)

	@staticmethod
	def get_engine(extension):
		
		ext = normalize_extension(extension)

		if EngineRegistry.engines.has_key(ext):
			return unique_list(EngineRegistry.engines[ext])
		else:
			return []