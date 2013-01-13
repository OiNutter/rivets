from lean.template import Template

class RJSMinCompressor(Template):

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
