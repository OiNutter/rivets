import regex as re

from lean.template import Template

class SafetyColons(Template):

	def prepare(self):
		pass


	def evaluate(self,scope, locals, block=None):
		#self.data = re.sub('\A[\n\r\s]+','',self.data)
		blank_pattern = re.compile(r"""\A\s*\Z""",re.M)
		end_pattern = re.compile(r""";\s*\Z""",re.M)

		if re.search(blank_pattern,self.data) or re.search(end_pattern,self.data):
			return self.data #return "%s\n" % self.data if self.data != "" and not self.data.endswith('\n') else self.data			
		else:
			return "%s;\n" % self.data