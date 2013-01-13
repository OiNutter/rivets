import re
from lean.template import Template

class DirectiveProcessor(Template):

	HEADER_PATTERN = re.compile(r"""\A(
										(/\* (.*) \*/) |
										(\#\#\# (.*) \#\#\#) |
										(// [^\n\r]* (?:\n)?)+ |
										(\# [^\n\r]* (?:\n)?)+
									)+""",re.S|re.X|re.M)

	DIRECTIVE_PATTERN = re.compile(r"""
										^ [\W]* = \s* (\w+.*?) (?:\*\/)? $
									""",re.X|re.M)

	def prepare(self):

		matches = self.HEADER_PATTERN.search(self.data)
		self.header = matches.group(0) if matches else ''

		self.body = self.data.replace(self.header,'')

		if not self.body.endswith('\n'):
			self.body += '\n'

		self.included_pathnames = []

	def evaluate(self,scope, locals, block=None):
		self.context = scope
		self.result = ""
		self.has_written_body = False

		self.process_directives()
		self.process_source()

		return self.result

	def get_processed_header(self):

		processed_header = []

		line_no = 0
		for line in self.header.split('\n'):
			line_no += 1
			match = False
			for directive in self.directives:
				if directive[0] == line_no:
					match = True
			
			processed_header.append('\n' if match else line)
			
		return ''.join(processed_header).strip()


	def process_source(self):

		processed_header = self.get_processed_header()
		if processed_header != "" and not self.has_written_body:
			self.result += processed_header + "\n"

		for path in self.included_pathnames:
			self.result += self.context.evaluate(path)

		if not self.has_written_body:
			self.result += self.body


	def find_directives(self):
	
		self.directives = []
		for index,line in enumerate(self.header.split('\n')):
			matches = self.DIRECTIVE_PATTERN.search(line)
			if matches:
				name,args = self.parse_directive(matches.group(1))
				if hasattr(self,'process_%s_directive'%name):
					self.directives.append((index+1,name,args))

		return self.directives

	def process_directives(self):
		directives = self.find_directives()
		for directive in directives:
			self.context.line = directive[0]
			getattr(self,'process_%s_directive'%directive[1])(directive[2])
			self.context.line = None

	def parse_directive(self,directive):
		comments_pattern = re.compile(r"[\\\"\\\'\\\n\\\r]")
		stripped = comments_pattern.sub('',directive)
		return stripped.strip().split(' ')

	def strip_directives(self,data):

		header = DirectiveProcessor.HEADER_PATTERN.findall(data)

		for line in header:
			
			matches = re.findall(DirectiveProcessor.DIRECTIVE_PATTERN,line[0])

			if matches:
				data = re.sub(re.escape(line[0]),'',data,re.X|re.S|re.M)

		# remove whitespace and new lines
		data = re.sub('\A[\n\r\s]+|[\n\r\s]+\Z','',data)
		return data

	def process_require_directive(self,path):
		return self.context.require_asset(path)

