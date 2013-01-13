from lean.template import Template

class UglipyJSCompressor(Template):

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