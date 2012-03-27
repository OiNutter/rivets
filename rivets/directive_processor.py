import re
import shlex

class DirectiveProcessor:

	HEADER_PATTERN = re.compile(r"""(
									(//.*(?:\\n)?) |
									(\\\#.*(?:\\n))
								)+""",re.X)

	DIRECTIVE_PATTERN = re.compile(r"""
							^ [\W]* = \s* (\w+.*?) (?:\*\/)? $
							""",re.X)

	@staticmethod
	def find_directives(content):
		headers = re.findall(DirectiveProcessor.HEADER_PATTERN, content)
		directives = []
		for header in headers:
			directives.extend(re.findall(DirectiveProcessor.DIRECTIVE_PATTERN,header[0]))
		directives[:] = [DirectiveProcessor.parse_directive(directive) for directive in directives]
		print '### DIRECTIVES ###'
		print directives
		return directives

	@staticmethod
	def parse_directive(directive):
		directive = [directive]
		directive.extend(shlex.split(directive[0],True))
		return directive
