import re

class DirectiveProcessor:

	HEADER_PATTERN = re.compile(r"""\A(
										(/\* (.*) \*/) |
										(\#\#\# (.*) \#\#\#) |
										(// [^\n\r]* (\n)?)+ |
										(\# [^\n\r]* (\n)?)+
									)+""",re.S|re.X)

	DIRECTIVE_PATTERN = re.compile(r"""
										^ [\W]* = \s* (\w+.*?) (?:\*\/)? $
									""",re.X|re.M)

	
	@staticmethod
	def find_directives(data):
		
		directives = []

		header = DirectiveProcessor.HEADER_PATTERN.findall(data)

		for line in header:

			matches = re.findall(DirectiveProcessor.DIRECTIVE_PATTERN,line[0])
			
			for match in matches:
				directives.append(DirectiveProcessor.parse_directive(match))

		return directives



	@staticmethod
	def parse_directive(directive):
		comments_pattern = re.compile(r"[\\\"\\\'\\\n\\\r]")
		stripped = comments_pattern.sub('',directive)
		directive = [directive]
		directive.extend(stripped.split(' '))
		return directive

	@staticmethod
	def strip_directives(data):

		header = DirectiveProcessor.HEADER_PATTERN.findall(data)

		for line in header:
			
			matches = re.findall(DirectiveProcessor.DIRECTIVE_PATTERN,line[0])

			if matches:
				data = re.sub(re.escape(line[0]),'',data,re.X|re.S|re.M)

		# remove whitespace and new lines
		data = re.sub('\A[\n\r\s]+|[\n\r\s]+\Z','',data)
		return data

