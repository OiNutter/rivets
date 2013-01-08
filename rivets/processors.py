from extensions import normalize_extension
from lean.template import Template

class ProcessorRegistry:

	# list of processors to be run before or after engine processors
	processors = {
		"pre":{},
		"post":{}
	}

	# special list of post processors to be run as the last processors
	minifiers = {}

	@staticmethod
	def register_preprocessor(extension,processor):
		ProcessorRegistry.register_processor('pre',extension,processor)

	@staticmethod
	def register_postprocessor(extension,processor):
		ProcessorRegistry.register_processor('post',extension,processor)

	@staticmethod
	def register_processor(position,extension,processor):
		ext = normalize_extension(extension)
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
		ext = normalize_extension(extension)
		if ProcessorRegistry.processors[position].has_key(ext):
			return ProcessorRegistry.processors[position][ext]
		else:
			return []

	@staticmethod
	def set_minifier(extension,processor):
		ext = normalize_extension(extension)
		ProcessorRegistry.minifiers[ext] = processor

	@staticmethod
	def get_minifier(extension):
		ext = normalize_extension(extension)
		return ProcessorRegistry.minifiers[ext] if ProcessorRegistry.minifiers.has_key(ext) else None

class UglipyJSProcessor(Template):

	@staticmethod
	def is_engine_initialized():
		return 'uglipyjs' in globals()

	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			import uglipyjs
			self.output = uglipyjs.compile(self.data)

		return self.output

class RJSMinProcessor(Template):

	@staticmethod
	def is_engine_initialized():
		return 'rjsmin' in globals()

	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			from rjsmin import jsmin
			self.output = jsmin(self.data)

		return self.output

class SlimitProcessor(Template):

	@staticmethod
	def is_engine_initialized():
		return 'slimit' in globals()

	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			from slimit import minify
			self.output = minify(self.data, mangle=True, mangle_toplevel=False)

		return self.output

class CSSMinProcessor(Template):

	@staticmethod
	def is_engine_initialized():
		return 'cssmin' in globals()

	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			from cssmin import cssmin
			self.output = cssmin(self.data)

 		return self.output

class SlimmerCSSProcessor(Template):

	@staticmethod
	def is_engine_initialized():
		return 'slimmer_css' in globals()

	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			from slimmer import css_slimmer
			self.output = css_slimmer(self.data)

		return self.output

class SlimmerJSProcessor(Template):

	@staticmethod
	def is_engine_initialized():
		return 'slimmer_js' in globals()

	def prepare(self):
		pass

	def evaluate(self,scope, locals, block=None):
		if not hasattr(self,'output') or not self.output:
			from slimmer import js_slimmer
			self.output = js_slimmer(self.data)

		return self.output