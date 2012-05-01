from shift.template import Template

class Processor(Template):
	''' `Processor` creates an anonymous processor class from a block.
 		
 		register_preprocessor(my_processor, lambda context, data: # ...
  	'''

	def __init__(self,name,processor):
		self._name = name
		self.processor = processor

	def name(self):
		return "rivets.processor.Processor (%s)" % self._name
	
	def to_string(self):
		return self.name

	def prepare(self):
		return 

	def evaluate(self,context, locals):
		''' Call processor block with `context` and `data`. '''
		return self.processor(context, self.data)