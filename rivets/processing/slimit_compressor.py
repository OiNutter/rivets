from lean.template import Template

class SlimitCompressor(Template):

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