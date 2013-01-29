import os
import regex as re

from errors import ContentTypeMismatch,FileNotFound
import utils

class Context(object):

	def __init__(self,environment,logical_path,pathname):
		self.environment = environment
		self._logical_path = logical_path
		self.pathname = pathname
		self.line = None
		self.object_id = id(self)

		self.required_paths = []
		self.stubbed_assets = []
		self.dependency_paths = []
		self.dependency_assets = [pathname]

	@property
	def root_path(self):
		for path in self.environment.paths:
			if re.search(re.escape(path),self.pathname):
				return path
		return ""

	@property
	def logical_path(self):
		filename,extname = os.path.splitext(self._logical_path)
		return re.sub(r"""%s$"""%extname,'',self._logical_path)

	@property
	def content_type(self):
		return self.environment.get_content_type_of(self.pathname)

	def evaluate(self,path,**options):
	
		pathname = self.resolve(path)
		attributes = self.environment.get_attributes_for(pathname)
		processors = options['processors'] if options.has_key('processors') else attributes.processors

		if options.has_key('data'):
			result = options['data']
		else:
			if hasattr(self.environment,'default_encoding'):
				filename,ext = os.path.splitext(pathname)
				encoding = self.environment.default_encoding
				result = utils.read_unicode(pathname,encoding)
			else:
				result = utils.read_unicode(pathname)

		for processor in processors:
			try:
				template = processor(pathname,block=lambda x: result)
				result = template.render(self,{})

			except Exception,e:
				self.annotate_exception(e)

		return result

	def resolve(self,path,**options):
		attributes = self.environment.get_attributes_for(path)

		if os.path.isabs(path):
			if self.environment.stat(path):
				return path
			else:
				raise FileNotFound("Couldn't find file %s" % path)

		elif options.has_key('content_type') and options['content_type']:
			content_type = self.content_type if options['content_type'] == 'self' else options['content_type']
			if attributes.format_extension:
				attr_content_type = attributes.content_type
				if content_type != attr_content_type:
					raise ContentTypeMismatch("%s is '%s', not '%s'"%(path,attr_content_type,content_type))

			def return_candidate(candidate):
 				if self.content_type == self.environment.get_content_type_of(candidate):
					return candidate
			
			asset = self.resolve(path,callback=return_candidate)
			if asset:
				return asset

			raise FileNotFound("Couldn't find file %s" % path)

		else:
			options['base_path'] = os.path.dirname(self.pathname)
			return self.environment.resolve(path,**options)

	def depend_on(self,path):
		self.dependency_paths.append(self.resolve(path))

	def depend_on_asset(self,path):
		filename = self.resolve(path)
		if filename:
			self.dependency_assets.append(filename)

	def require_asset(self,path):
		pathname = self.resolve(path,content_type='self')
		if pathname:
			self.depend_on_asset(pathname)
			self.required_paths.append(pathname)

	def stub_asset(self,path):
		self.stubbed_assets.append(self.resolve(path,content_type ='self'))

	def is_asset_requirable(self,path):
		pathname = self.resolve(path)
		content_type = self.environment.get_content_type_of(pathname)
		requirable = False
		if os.path.exists(pathname) and os.path.isfile(pathname):
			if self.content_type and content_type == self.content_type:
				requirable = True
		
		return requirable

	def annotate_exception(self,exception):
		location = self.pathname
		location += ":%s" % self.line if self.line else ''

		raise exception.__class__("%s (in %s)" % (str(exception),location))
