import re

from lean.template import Template

class CharsetNormalizer(Template):

	def prepare(self):
		pass

	def evaluate(self,context,locals,callback=None):
		charset = None

		charset_pattern = re.compile(r"""^@charset "([^"]+)";$""",re.M)
		charsets = charset_pattern.findall(self.data)

		for match in charsets:
			if not charset:
				charset = match

		filtered_data = charset_pattern.sub("",self.data)

		if charset:
			return '@charset "%s";%s' % (charset,filtered_data)
		else:
			return self.data



