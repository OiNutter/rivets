from lean.template import Template

class Processor(Template):

	def __str__(self):
		return self.name

	def prepare(self):
		pass

	def evaluate(self,context,local_vars,callback=None):
		return self.processor(context,self.data)