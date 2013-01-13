import re

from lean.template import Template

class SafetyColons(Template):

	def prepare(self):
		pass


	def evaluate(self,scope, locals, block=None):
		self.data = re.sub('\A[\n\r\s]+|[\n\r\s]+\Z','',self.data)
		blank_pattern = re.compile(r"""\A[\s\n\r]*\Z""",re.X)
		end_pattern = re.compile(r""";[\s\n\r]*\Z""",re.X)

		if re.search(blank_pattern,self.data) or re.search(end_pattern,self.data):
			return self.data
		else:
			return "%s;" % self.data