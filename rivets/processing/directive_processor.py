import regex as re
from lean.template import Template

class DirectiveProcessor(Template):

	HEADER_PATTERN = re.compile(r"""\A (
									(?m:\s*)(
											(/\* (?m:.*?) \*/) |
											(\#\#\# (?m:.*?) \#\#\#) |
											(// [^\n\r]*)+ |
											(\# [^\n\r]*)+
										)	
									)+
									""",re.X|re.S|re.V1)

	DIRECTIVE_PATTERN = re.compile(r"""
										^ [\W]* = \s* (\w+.*?) (?:\*/)? $
									""",re.X)

	def prepare(self):
		matches = self.HEADER_PATTERN.match(self.data)
		self.header = matches.group(0) if matches else ''
		self.body = re.sub(re.escape(self.header) + "\n?",'',self.data,1)
		
		if self.body != "" and not self.body.endswith('\n'):
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
		for line in self.header.splitlines(True):
			line_no += 1
			match = False
			for directive in self.directives():
				if directive[0] == line_no:
					match = True
			
			processed_header.append('\n' if match else line)

		header = ''.join(processed_header).rstrip('\n')

		return header + '\n' if header != "" else ""

	def get_processed_source(self):
		if not hasattr(self,'processed_source'):
			self.processed_source = self.get_processed_header() + self.body

		return str(self.processed_source)


	def process_source(self):

		processed_header = self.get_processed_header()

		if processed_header != "" and not self.has_written_body:
			self.result += processed_header + "\n"

		for path in self.included_pathnames:
			self.result += self.context.evaluate(path)

		if not self.has_written_body:
			self.result += self.body


	def directives(self):
	
		directives = []
		for index,line in enumerate(self.header.split('\n')):
			matches = self.DIRECTIVE_PATTERN.search(line)
			if matches:
				parsed = self.parse_directive(matches.group(1))
				if parsed:
					name = parsed[0]
					args = parsed[1:]
					if hasattr(self,'process_%s_directive'%name):
						directive = [index+1,str(name)]
						directive.extend([str(arg) for arg in args])
						directives.append(tuple(directive))

		return directives

	def process_directives(self):
		directives = self.directives()
		for directive in directives:
			self.context.line = directive[0]
			getattr(self,'process_%s_directive'%directive[1])(directive[2])
			self.context.line = None

	def parse_directive(self,directive):
		comments_pattern = re.compile(r"[\\\"\\\'](.+)[\\\"\\\']")
		args = comments_pattern.findall(directive)
		stripped = comments_pattern.sub('',directive)
		parsed = stripped.strip().split(' ')
		parsed.extend(args)
		return parsed

	def process_require_directive(self,path):
		return self.context.require_asset(path)

