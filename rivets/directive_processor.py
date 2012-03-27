import re
import shlex

class DirectiveProcessor:

	HEADER_PATTERN = re.compile(r"""(
									(\\\#\\\#\\\# \\n?(.*?)\\n? \\\#\\\#\\\#) |
									(//.*(?:\\n)?) |
									(\\\#.*(?:\\n))
								)+""",re.X)

	DIRECTIVE_PATTERN = re.compile(r"""
							^ [\W]* = \s* (\w+.*?) (?:\*\/)? $
							""",re.X)

	@staticmethod
	def find_directives(file):
		directives = {}
		i=1
		for line in file:
			if re.search(DirectiveProcessor.HEADER_PATTERN,line):
				match = re.search(DirectiveProcessor.DIRECTIVE_PATTERN,line)

				if match:
					print match.group(1)
					directives[i] = DirectiveProcessor.parse_directive(match.group(1))

			i = i+1

		file.seek(0)
		print '### DIRECTIVES ###'
		print directives
		return directives

	@staticmethod
	def parse_directive(directive):
		comments_pattern = re.compile(r"[\\\"\\\'\\\n\\\r]")
		stripped = comments_pattern.sub('',directive)
		directive = [directive]
		directive.extend(stripped.split(' '))
		return directive
