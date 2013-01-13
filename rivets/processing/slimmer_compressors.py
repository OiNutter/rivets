from lean.template import Template

class SlimmerCSSCompressor(Template):

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

class SlimmerJSCompressor(Template):

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