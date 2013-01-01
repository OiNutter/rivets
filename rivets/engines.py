import extensions
from shift.template import Template
from errors import EngineError

class EngineRegistry:

	engines = {}

	@staticmethod
	def register_engine(extension,engine):

		ext = extensions.normalize_extension(extension)
		if not EngineRegistry.engines.has_key(ext):
			EngineRegistry.engines[ext] = engine

	@staticmethod
	def get_engine(extension):
		if EngineRegistry.engines.has_key(extension):
			return EngineRegistry.engines[extension]
		else:
			raise EngineError("Unable to find an engine for file extension: %s"%extension)

class JSTemplate(Template):

	default_mime_type = 'application/javascript'

	default_bare = False

	@staticmethod
	def is_engine_initialized():
		return 'javascript' in globals()

	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			self.output = self.data

		return self.output

class CSSTemplate(Template):

	default_mime_type = 'text/css'

	@staticmethod
	def is_engine_initialized():
		return 'css' in globals()
	
	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			self.output = self.data

		return self.output

