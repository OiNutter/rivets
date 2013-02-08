import os
import regex as re

from lean.template import Template

from ..errors import ArgumentError

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
		
		if self.body != "" and not re.search(r"""\n\Z""",self.body,re.M):
			self.body += '\n'

		self.included_pathnames = []

	def evaluate(self,scope, locals, block=None):
		self.context = scope
		self.result = ""
		self.has_written_body = False

		self.process_directives()
		self.process_source()

		return self.result

	@property
	def processed_header(self):

		processed_header = []

		line_no = 0
		for line in self.header.splitlines(True):
			line_no += 1
			match = False
			for directive in self.directives:
				if directive[0] == line_no:
					match = True
			
			processed_header.append('\n' if match else line)

		header = ''.join(processed_header).rstrip('\n')

		return header + '\n' if not re.search(r"""\A\s*\Z""",header,re.M) else ""

	@property
	def processed_source(self):
		if not hasattr(self,'_processed_source'):
			self._processed_source = self.processed_header + self.body

		return str(self._processed_source)


	def process_source(self):

		processed_header = self.processed_header

		if processed_header != "" and not self.has_written_body:
			self.result += processed_header + "\n"

		for path in self.included_pathnames:
			self.result += self.context.evaluate(path)
			
		if not self.has_written_body:
			self.result += self.body

	@property
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
		directives = self.directives
		for directive in directives:
			self.context.line = directive[0]
			getattr(self,'process_%s_directive'%directive[1])(*directive[2:])
			self.context.line = None

	def parse_directive(self,directive):
		comments_pattern = re.compile(r"[\\\"\\\'](.+)[\\\"\\\']")
		args = comments_pattern.findall(directive)
		stripped = comments_pattern.sub('',directive)
		parsed = stripped.strip().split(' ')
		parsed.extend(args)
		return parsed

	def process_require_directive(self,path):
		self.context.require_asset(path)

	def process_require_self_directive(self):
		if self.has_written_body:
			raise ArgumentError('require_self can only be called once per source file')

		self.context.require_asset(self._file)
		self.process_source()
		self.included_pathnames = []
		self.has_written_body = True

	def process_include_directive(self,path):
		pathname = self.context.resolve(path)
		self.context.depend_on_asset(pathname)
		self.included_pathnames.append(pathname)

	def process_require_directory_directive(self,path="."):
		if is_relative_path(path):
			root = os.path.join(
							os.path.dirname(self._file),
							path
						)
			root = os.path.realpath(root)
			print 'ROOT: ', root

			stats = self.stat(root)
			if not stats or not os.path.isdir(root):
				raise ArgumentError("require_directory argument must be a directory")

			self.context.depend_on(root)
			print 'FILE: ', self._file
			for pathname in self.entries(root):
				print 'PATH: ',pathname
				pathname = os.path.join(root,pathname)
				if pathname ==self._file:
					continue
				elif self.context.is_asset_requirable(pathname):
					self.context.require_asset(pathname)

		else:
			raise ArgumentError('require_directory argument must be a relative path')

	def process_require_tree_directive(self,path="."):
		if is_relative_path(path):
			root = os.path.join(
							os.path.dirname(self._file),
							path
						)
			root = os.path.realpath(root)

			stats = self.stat(root)
			if not stats or not os.path.isdir(root):
				raise ArgumentError("require_directory argument must be a directory")

			self.context.depend_on(root)

			def do_require(pathname,*args):
				if pathname == self._file:
					return
				elif os.path.isdir(pathname):
					self.context.depend_on(pathname)
				elif self.context.is_asset_requirable(pathname):
					self.context.require_asset(pathname)

			self.each_entry(root,callback=do_require)

		else:
			raise ArgumentError("require_tree argument must be a relative path")

	def process_depend_on_directive(self,path):
		self.context.depend_on(path)

	def process_depend_on_asset_directive(self,path):
		self.context.depend_on_asset(path)

	def process_stub_directive(self,path):
		self.context.stub_asset(path)

	def stat(self,path):
		return self.context.environment.stat(path)

	def entries(self,path):
		return self.context.environment.entries(path)

	def each_entry(self,root,callback=None):
		return self.context.environment.each_entry(root,callback)

def is_relative_path(path):
	return True if re.match(r"""^\.($|\.?\/)""",path) else False




