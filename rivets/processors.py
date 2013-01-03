import uglipyjs

import extensions
from shift.template import Template

class ProcessorRegistry:

	processors = {
		"pre":{},
		"post":{}
	}

	@staticmethod
	def register_preprocessor(extension,processor):
		ProcessorRegistry.register_processor('pre',extension,processor)

	@staticmethod
	def register_postprocessor(extension,processor):
		ProcessorRegistry.register_processor('post',extension,processor)

	@staticmethod
	def register_processor(position,extension,processor):
		ext = extensions.normalize_extension(extension)
		if not ProcessorRegistry.processors[position].has_key(ext):
			ProcessorRegistry.processors[position][ext] = []

		ProcessorRegistry.processors[position][ext].append(processor)

	@staticmethod
	def get_preprocessors(extension):
		return ProcessorRegistry.get_processors('pre',extension)

	@staticmethod
	def get_postprocessors(extension):
		return ProcessorRegistry.get_processors('post',extension)

	@staticmethod
	def get_processors(position,extension):
		if ProcessorRegistry.processors[position].has_key(extension):
			return ProcessorRegistry.processors[position][extension]
		else:
			return []

class UglipyJSProcessor(Template):

	@staticmethod
	def is_engine_initialized():
		return 'uglipyjs' in globals()

	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			self.output = uglipyjs.compile(self.data)

		return self.output

