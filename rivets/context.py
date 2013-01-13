import os
import re
import io

from errors import ContentTypeMismatch

class Context:

	def __init__(self,environment,logical_path,pathname):
		self.environment = environment
		self.logical_path = logical_path
		self.pathname = pathname
		self.line = None

		self.required_paths = []
		self.stubbed_assets = []
		self.dependency_paths = []
		self.dependency_assets = [pathname]

	def root_path(self):
		for path in self.environment.paths:
			if re.search(re.escape(path),self.pathname):
				return path
		return ""

	def logical_path(self):
		filename,extname = os.path.splitext(self.logical_path)
		return re.sub(r"""%s$"""%extname,'',self.logical_path)

	def content_type(self):
		return self.environment.get_content_type_of(self.pathname)

	def evaluate(self,path,options=None):

		if not options:
			options = {}

		pathname = self.resolve(path)
		attributes = self.environment.get_attributes_for(pathname)
		processors = options['processors'] if options.has_key('processors') else attributes.get_processors()

		if options.has_key('data'):
			result = options['data']
		else:
			if hasattr(self.environment,'default_encoding'):
				filename,ext = os.path.splitext(pathname)
				encoding = self.environment.default_encoding
				result = io.open(pathname,encoding=encoding).read()
			else:
				result = io.open(pathname,encoding='UTF-8').read()

		for processor in processors:
			try:
				template = processor(pathname,block=lambda x: result)
				result = template.render(self,{})
			except Exception,e:
				raise Exception(self.annotate_exception(e))

		return result

	def resolve(self,path,options=None, callback=None):
		attributes = self.environment.get_attributes_for(path)

		if not options:
			options = {}

		if os.path.isabs(path):
			if os.stat(path):
				return path
			else:
				raise IOError("Couldn't find file %s" % path)

		elif options and options['content_type']:
			content_type = self.content_type() if options['content_type'] == 'self' else options['content_type']
			if attributes.get_format_extension():
				attr_content_type = attributes.get_content_type() 
				if content_type != attr_content_type:
					raise ContentTypeMismatch("%s is %s, not %s"%(path,attr_content_type,content_type))

			def return_candidate(candidate):
				if self.content_type() == self.environment.get_content_type_of(candidate):
					return candidate
			
			return self.resolve(path,callback=return_candidate)

			raise IOError("Couldn't find file %s" % path)

		else:
			return self.environment.resolve(path,{'base_path':os.path.dirname(self.pathname)}.update(options),callback)

	def depend_on(self,path):
		self.dependency_paths.append(self.resolve(path))

	def depend_on_asset(self,path):
		filename = self.resolve(path)
		self.dependency_assets.append(filename)

	def require_asset(self,path):
		pathname = self.resolve(path,{'content_type':'self'})
		self.depend_on_asset(pathname)
		self.required_paths.append(pathname)

	def stub_asset(self,path):
		self.stubbed_assets.add(self.resolve(path,{'content_type':'self'}))

	def is_asset_requirable(self,path):
		pathname = self.resolve(path)
		content_type = self.environment.get_content_type_of(pathname)
		requirable = False
		if os.path.exists(pathname) and os.path.isfile(pathname):
			if self.content_type() and content_type == self.content_type():
				requirable = True
		
		return requirable

	def annotate_exception(self,exception):
		location = self.pathname
		location += ":%s" if self.line else ''

		return "%s (in %s)" % (str(exception),location)
