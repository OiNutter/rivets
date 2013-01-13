from lean.template import Template

class CSSMinCompressor(Template):

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